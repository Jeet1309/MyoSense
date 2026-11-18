#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <math.h>

// ============================================
// TEAM KRESIT - MUSCLE BIOAMP CANDY
// ESP32-S3 N16R8
// SINGLE CHANNEL EMG - BLE STREAM + BATTERY
//
// Same sampling and MVC logic as team_mvc.ino,
// plus a Nordic-UART-style BLE service and
// battery / charging telemetry.
// ============================================

// ---- EMG ----
#define EMG_PIN 4

const uint32_t SAMPLE_RATE = 2000;
const uint32_t SAMPLE_INTERVAL_US = 500;
const uint16_t WINDOW_SIZE = 200;

// ---- Battery ----
// Divider: cell + --[ R1 100k ]-- node --[ R2 100k ]-- GND
// node -> BATT_PIN.  Ratio = (R1 + R2) / R2 = 2.0
#define BATT_PIN 1              // ADC1_CH0
const float BATT_DIVIDER = 2.0f;
const uint32_t BATT_INTERVAL_MS = 1000;

// Charging indicator (optional).
// The HW-373 CHRG pad sinks to GND while charging, but that pad sits behind an
// LED tied to the 5 V rail, so probing it directly can put >3.3 V on a GPIO.
// Leave this at -1 until you have a 10k series resistor to 3V3 and have measured
// the pad voltage. With -1 the firmware infers charging from a rising pack voltage.
#define CHRG_PIN -1

// ---- BLE ----
#define DEVICE_NAME  "MyoSense-EMG"
#define SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define RX_UUID      "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define TX_UUID      "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// ---- Signal processing state ----
double sumSignal = 0.0;
double sumSquares = 0.0;

uint16_t sampleCount = 0;

float rms_mV = 0.0;
float mean_mV = 0.0;

bool calibrating = false;
uint32_t calibrationStart = 0;

float mvc_mV = 0.0;
float calibrationMax = 0.0;

uint32_t nextSample = 0;

// ---- Battery state ----
float batt_mV = 0.0;
float batt_mV_smooth = 0.0;
int batt_pct = -1;
bool charging = false;
bool chargingInferred = false;

uint32_t nextBattRead = 0;
float battHistory[8];
uint8_t battHistoryCount = 0;
uint8_t battHistoryIndex = 0;

// ---- BLE state ----
BLEServer *pServer = NULL;
BLECharacteristic *pTx = NULL;
BLECharacteristic *pRx = NULL;

bool deviceConnected = false;
bool wasConnected = false;

// ---- Diagnostics ----
uint16_t windowsThisSecond = 0;
uint16_t windowsLastSecond = 0;
uint32_t lastRateMark = 0;

// ============================================
// BATTERY
// ============================================

// Piecewise Li-ion open-circuit curve: 3.30 V empty, 4.20 V full.
int batteryPercent(float mV) {

  struct Point {
    float mv;
    int pct;
  };

  static const Point curve[] = {
    { 4200, 100 }, { 4100, 90 }, { 4000, 80 },
    { 3900, 65 },  { 3800, 50 }, { 3700, 35 },
    { 3600, 20 },  { 3500, 10 }, { 3400, 5 },
    { 3300, 0 }
  };

  const int n = sizeof(curve) / sizeof(curve[0]);

  if (mV >= curve[0].mv) return 100;
  if (mV <= curve[n - 1].mv) return 0;

  for (int i = 0; i < n - 1; i++) {
    if (mV <= curve[i].mv && mV >= curve[i + 1].mv) {
      float span = curve[i].mv - curve[i + 1].mv;
      float t = (mV - curve[i + 1].mv) / span;
      return (int)(curve[i + 1].pct + t * (curve[i].pct - curve[i + 1].pct));
    }
  }

  return 0;
}

void updateBattery() {

  if ((int32_t)(millis() - nextBattRead) < 0) return;

  nextBattRead = millis() + BATT_INTERVAL_MS;

  // Average a small burst so the ADC noise does not
  // make the percentage jump around.
  uint32_t acc = 0;

  for (uint8_t i = 0; i < 8; i++) {
    acc += analogReadMilliVolts(BATT_PIN);
    delayMicroseconds(200);
  }

  batt_mV = (acc / 8.0f) * BATT_DIVIDER;

  if (batt_mV_smooth < 1.0f) {
    batt_mV_smooth = batt_mV;
  } else {
    batt_mV_smooth = batt_mV_smooth * 0.8f + batt_mV * 0.2f;
  }

  batt_pct = batteryPercent(batt_mV_smooth);

  // --- charging state ---
  if (CHRG_PIN >= 0) {

    // HW-373 CHRG pad: pulled low while a charge is in progress.
    // Guard against the pin floating high on boards without the pad.
    charging = (digitalRead(CHRG_PIN) == LOW);

  } else {

    // Infer from the voltage trend over ~8 s.
    battHistory[battHistoryIndex] = batt_mV_smooth;
    battHistoryIndex = (battHistoryIndex + 1) % 8;

    if (battHistoryCount < 8) battHistoryCount++;

    if (battHistoryCount >= 8) {

      float oldest = battHistory[battHistoryIndex];
      float delta = batt_mV_smooth - oldest;

      chargingInferred = (delta > 20.0f);
      charging = chargingInferred;
    }
  }
}

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

  sumSignal = 0.0;
  sumSquares = 0.0;
  sampleCount = 0;

  updateCalibration();

  // Relative activation. Deliberately NOT clamped:
  // a value above 100% means the MVC reference is low.
  float activation = 0.0;

  if (mvc_mV > 0.01) {
    activation = (rms_mV / mvc_mV) * 100.0;
  }

  // Front-end sitting on a rail?
  bool clipped = (mean_mV > 3100.0 || mean_mV < 60.0);

  // ---- serial ----
  Serial.print("Mean: ");
  Serial.print(mean_mV, 2);
  Serial.print(" mV | RMS: ");
  Serial.print(rms_mV, 3);
  Serial.print(" mV | Activation: ");
  Serial.print(activation, 1);
  Serial.print("% | Batt: ");
  Serial.print(batt_mV_smooth / 1000.0f, 2);
  Serial.print(" V ");
  Serial.print(batt_pct);
  Serial.print("%");
  if (charging) Serial.print(" CHG");

  if (calibrating) Serial.print(" | CALIBRATING");

  Serial.println();

  // ---- BLE ----
  // mean,rms,activation,calibrating,batt_mV,batt_pct,charging,flags
  char line[64];

  snprintf(
      line,
      sizeof(line),
      "%.0f,%.2f,%.1f,%d,%.0f,%d,%d,%d\n",
      mean_mV,
      rms_mV,
      activation,
      calibrating ? 1 : 0,
      batt_mV_smooth,
      batt_pct,
      charging ? 1 : 0,
      clipped ? 1 : 0
  );

  notifyLine(line);

  // ---- sample-rate health ----
  windowsThisSecond++;

  if (millis() - lastRateMark >= 1000) {
    windowsLastSecond = windowsThisSecond;
    windowsThisSecond = 0;
    lastRateMark = millis();
  }
}

// ============================================
// SETUP
// ============================================

void setup() {

  Serial.begin(115200);

  delay(1500);

  analogReadResolution(12);

  analogSetPinAttenuation(EMG_PIN, ADC_11db);
  analogSetPinAttenuation(BATT_PIN, ADC_11db);

  pinMode(EMG_PIN, INPUT);

  if (CHRG_PIN >= 0) {
    pinMode(CHRG_PIN, INPUT_PULLUP);
  }

  nextSample = micros();
  nextBattRead = millis();

  Serial.println();
  Serial.println("================================");
  Serial.println(" TEAM KRESIT - CANDY EMG");
  Serial.println(" ESP32-S3 N16R8  (BLE + BATT)");
  Serial.println("================================");

  Serial.println("GPIO: 4");
  Serial.println("Sampling Rate: 2000 Hz");
  Serial.println("RMS Window: 100 ms");
  Serial.println("BLE name: MyoSense-EMG");
  Serial.println("Battery ADC: GPIO1 (divider x2)");

  Serial.println("--------------------------------");
  Serial.println("Send C for MVC calibration.");
  Serial.println("Send R to reset calibration.");
  Serial.println("--------------------------------");

  startBle();

  updateBattery();

  Serial.println("BLE advertising started.");
  Serial.print("Battery: ");
  Serial.print(batt_mV_smooth / 1000.0f, 2);
  Serial.print(" V  ");
  Serial.print(batt_pct);
  Serial.println("%");
  Serial.println("--------------------------------");
}

// ============================================
// MAIN LOOP
// ============================================

void loop() {

  if (Serial.available()) {

    char command = Serial.read();

    if (command == 'C' || command == 'c') {
      startCalibration();
    } else if (command == 'R' || command == 'r') {
      resetCalibration();
    }
  }

  if (deviceConnected != wasConnected) {

    wasConnected = deviceConnected;

    if (deviceConnected) {
      Serial.println("BLE client connected.");
    } else {
      Serial.println("BLE client disconnected - advertising again.");
    }
  }

  updateBattery();

  uint32_t currentTime = micros();

  if ((int32_t)(currentTime - nextSample) >= 0) {

    nextSample += SAMPLE_INTERVAL_US;

    float voltage = (float)analogReadMilliVolts(EMG_PIN);

    sumSignal += voltage;
    sumSquares += (double)voltage * voltage;
    sampleCount++;

    if (sampleCount >= WINDOW_SIZE) {
      calculateRMS();
    }

    if ((int32_t)(micros() - nextSample) >=
        (int32_t)SAMPLE_INTERVAL_US) {

      nextSample = micros() + SAMPLE_INTERVAL_US;
    }
  }
}
