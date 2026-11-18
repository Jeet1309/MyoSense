#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <math.h>

// ============================================
// TEAM KRESIT - MUSCLE BIOAMP CANDY
// ESP32-S3 N16R8
// SINGLE CHANNEL EMG - BLE STREAM
//
// Same sampling and MVC logic as team_mvc.ino,
// plus a Nordic-UART-style BLE service so the
// values arrive on a phone or laptop.
// ============================================

// Hardware configuration
#define EMG_PIN 4

// Sampling configuration
const uint32_t SAMPLE_RATE = 2000;
const uint32_t SAMPLE_INTERVAL_US = 500;

// 100 ms RMS window
const uint16_t WINDOW_SIZE = 200;

// BLE identity
#define DEVICE_NAME  "MyoSense-EMG"
#define SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define RX_UUID      "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define TX_UUID      "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// Signal processing variables
double sumSignal = 0.0;
double sumSquares = 0.0;

uint16_t sampleCount = 0;

float rms_mV = 0.0;
float mean_mV = 0.0;

// MVC calibration
bool calibrating = false;
uint32_t calibrationStart = 0;

float mvc_mV = 0.0;
float calibrationMax = 0.0;

// Sampling timer
uint32_t nextSample = 0;

// BLE state
BLEServer *pServer = NULL;
BLECharacteristic *pTx = NULL;
BLECharacteristic *pRx = NULL;

bool deviceConnected = false;
bool wasConnected = false;

// ============================================
// MVC CALIBRATION
// ============================================

void startCalibration() {

  calibrating = true;

  calibrationStart = millis();
  calibrationMax = 0.0;

  Serial.println();
  Serial.println("MVC CALIBRATION STARTED");
  Serial.println("Contract your target muscle.");
}

void resetCalibration() {

  calibrating = false;
  mvc_mV = 0.0;
  calibrationMax = 0.0;

  Serial.println();
  Serial.println("MVC RESET - activation back to 0%");
}

void updateCalibration() {

  if (!calibrating) return;

  if (rms_mV > calibrationMax) {
    calibrationMax = rms_mV;
  }

  if (millis() - calibrationStart >= 5000) {

    calibrating = false;
    mvc_mV = calibrationMax;

    Serial.println();
    Serial.println("MVC CALIBRATION COMPLETED");

    Serial.print("MVC RMS: ");
    Serial.print(mvc_mV, 3);
    Serial.println(" mV");
  }
}

// ============================================
// BLE
// ============================================

class ServerCallbacks : public BLEServerCallbacks {

  void onConnect(BLEServer *server) {
    deviceConnected = true;
  }

  void onDisconnect(BLEServer *server) {
    deviceConnected = false;
    BLEAdvertising *adv = BLEDevice::getAdvertising();
    adv->start();
  }
};

class RxCallbacks : public BLECharacteristicCallbacks {

  void onWrite(BLECharacteristic *characteristic) {

    size_t length = characteristic->getLength();

    if (length == 0) return;

    uint8_t *data = characteristic->getData();

    char command = (char)data[0];

    if (command == 'C' || command == 'c') {
      startCalibration();
    } else if (command == 'R' || command == 'r') {
      resetCalibration();
    }
  }
};

void startBle() {

  BLEDevice::init(DEVICE_NAME);
  BLEDevice::setMTU(247);

  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new ServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  pTx = pService->createCharacteristic(
      TX_UUID,
      BLECharacteristic::PROPERTY_NOTIFY
  );

  pTx->addDescriptor(new BLE2902());

  pRx = pService->createCharacteristic(
      RX_UUID,
      BLECharacteristic::PROPERTY_WRITE |
      BLECharacteristic::PROPERTY_WRITE_NR
  );

  pRx->setCallbacks(new RxCallbacks());

  pService->start();

  BLEAdvertising *pAdv = BLEDevice::getAdvertising();
  pAdv->addServiceUUID(SERVICE_UUID);
  pAdv->setScanResponse(true);
  pAdv->setMinPreferred(0x06);
  pAdv->setMinPreferred(0x12);
  pAdv->start();
}

// Notify one text line, split only if the client
// negotiated a small MTU.
void notifyLine(const char *text) {

  if (!deviceConnected || pTx == NULL) return;

  size_t length = strlen(text);

  uint16_t mtu = BLEDevice::getMTU();
  size_t chunk = (mtu > 23) ? (size_t)(mtu - 3) : 20;

  for (size_t offset = 0; offset < length; offset += chunk) {

    size_t n = length - offset;
    if (n > chunk) n = chunk;

    pTx->setValue((uint8_t *)(text + offset), n);
    pTx->notify();

    delay(4);
  }
}

// ============================================
// RMS CALCULATION
// ============================================

void calculateRMS() {

  if (sampleCount == 0) return;

  mean_mV = sumSignal / sampleCount;

  double variance =
      (sumSquares / sampleCount)
      - (mean_mV * mean_mV);

  if (variance < 0.0) {
    variance = 0.0;
  }

  rms_mV = sqrt(variance);

  // Reset window
  sumSignal = 0.0;
  sumSquares = 0.0;
  sampleCount = 0;

  // Update MVC calibration
  updateCalibration();

  // Calculate relative activation
  float activation = 0.0;

  if (mvc_mV > 0.01) {

    activation = (rms_mV / mvc_mV) * 100.0;
  }

  // ========================================
  // SERIAL OUTPUT
  // ========================================

  Serial.print("Mean: ");
  Serial.print(mean_mV, 2);

  Serial.print(" mV | RMS: ");
  Serial.print(rms_mV, 3);

  Serial.print(" mV | Activation: ");
  Serial.print(activation, 1);

  Serial.print("%");

  if (calibrating) {
    Serial.print(" | CALIBRATING");
  }

  Serial.println();

  // ========================================
  // BLE OUTPUT  (mean,rms,activation,cal)
  // ========================================

  char line[48];

  snprintf(
      line,
      sizeof(line),
      "%.0f,%.2f,%.1f,%d\n",
      mean_mV,
      rms_mV,
      activation,
      calibrating ? 1 : 0
  );

  notifyLine(line);
}

// ============================================
// SETUP
// ============================================

void setup() {

  Serial.begin(115200);

  delay(1500);

  analogReadResolution(12);

  analogSetPinAttenuation(
    EMG_PIN,
    ADC_11db
  );

  pinMode(EMG_PIN, INPUT);

  nextSample = micros();

  Serial.println();
  Serial.println("================================");
  Serial.println(" TEAM KRESIT - CANDY EMG");
  Serial.println(" ESP32-S3 N16R8  (BLE)");
  Serial.println("================================");

  Serial.println("GPIO: 4");
  Serial.println("Sampling Rate: 2000 Hz");
  Serial.println("RMS Window: 100 ms");
  Serial.println("BLE name: MyoSense-EMG");

  Serial.println("--------------------------------");
  Serial.println("Send C for MVC calibration.");
  Serial.println("Send R to reset calibration.");
  Serial.println("--------------------------------");

  startBle();

  Serial.println("BLE advertising started.");
  Serial.println("--------------------------------");
}

// ============================================
// MAIN LOOP
// ============================================

void loop() {

  // Read Serial commands
  if (Serial.available()) {

    char command = Serial.read();

    if (command == 'C' || command == 'c') {
      startCalibration();
    } else if (command == 'R' || command == 'r') {
      resetCalibration();
    }
  }

  // Report connect / disconnect once
  if (deviceConnected != wasConnected) {

    wasConnected = deviceConnected;

    if (deviceConnected) {
      Serial.println("BLE client connected.");
    } else {
      Serial.println("BLE client disconnected - advertising again.");
    }
  }

  // Maintain sampling interval
  uint32_t currentTime = micros();

  if ((int32_t)(currentTime - nextSample) >= 0) {

    nextSample += SAMPLE_INTERVAL_US;

    // Read sensor output in millivolts
    float voltage =
        (float)analogReadMilliVolts(EMG_PIN);

    // Accumulate samples
    sumSignal += voltage;

    sumSquares +=
        (double)voltage * voltage;

    sampleCount++;

    // Process every 200 samples
    if (sampleCount >= WINDOW_SIZE) {
      calculateRMS();
    }

    // Recover if sampling falls behind
    if ((int32_t)(micros() - nextSample) >=
        (int32_t)SAMPLE_INTERVAL_US) {

      nextSample = micros() + SAMPLE_INTERVAL_US;
    }
  }
}
