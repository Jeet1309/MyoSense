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
// Three-press calibration:
//   1) rest baseline, 5 s relaxed
//   2) MVC, 5 s maximal
//   3) MVC verify, 5 s maximal (keeps the better)
//
// Activation is computed after removing the rest
// baseline in quadrature, so rest reads near 0%.
// ============================================

// ---- EMG ----
#define EMG_PIN 4

const uint32_t SAMPLE_RATE = 2000;
const uint32_t SAMPLE_INTERVAL_US = 500;
const uint16_t WINDOW_SIZE = 200;

// ---- Battery ----
// Divider: cell + --[ R1 68k ]-- node --[ R2 68k ]-- GND
// node -> BATT_PIN.  Ratio = (R1 + R2) / R2 = 2.0
#define BATT_PIN 1              // ADC1_CH0
const float BATT_DIVIDER = 2.0f;
const uint32_t BATT_INTERVAL_MS = 1000;

// Charging indicator (optional).
// The HW-373 CHRG pad sinks to GND while charging, but that pad sits behind an
// LED tied to the 5 V rail, so probing it directly can put >3.3 V on a GPIO.
// With -1 the firmware infers charging from a rising pack voltage.
#define CHRG_PIN -1

// ---- BLE ----
#define DEVICE_NAME  "MyoSense-EMG"
#define SERVICE_UUID "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
#define RX_UUID      "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define TX_UUID      "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

// ---- Signal processing ----
double sumSignal = 0.0;
double sumSquares = 0.0;

uint16_t sampleCount = 0;

float rms_mV = 0.0;
float mean_mV = 0.0;

uint32_t nextSample = 0;

// ---- Calibration state ----
enum CalStage {
  CAL_IDLE = 0,
  CAL_REST,
  CAL_MVC,
  CAL_VERIFY
};

CalStage calStage = CAL_IDLE;

float rest_mV = 0.0;        // measured noise floor
float mvc_mV = 0.0;         // maximal voluntary contraction

float calSum = 0.0;
uint16_t calCount = 0;
float calMax = 0.0;
uint32_t calibrationStart = 0;

const uint32_t CAL_DURATION_MS = 5000;

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

  if (batt_mV_smooth < 2600.0f) {
    batt_pct = -1;
  }

  if (CHRG_PIN >= 0) {

    charging = (digitalRead(CHRG_PIN) == LOW);

  } else {

    battHistory[battHistoryIndex] = batt_mV_smooth;
    battHistoryIndex = (battHistoryIndex + 1) % 8;

    if (battHistoryCount < 8) battHistoryCount++;

    if (battHistoryCount >= 8) {
      float oldest = battHistory[battHistoryIndex];
      chargingInferred = ((batt_mV_smooth - oldest) > 20.0f);
      charging = chargingInferred;
    }
  }
}

// ============================================
// CALIBRATION - three presses of 'C'
// ============================================

// Press 1 -> rest, press 2 -> MVC, press 3 -> verify, then it cycles.
void advanceCalibration() {

  calSum = 0.0;
  calCount = 0;
  calMax = 0.0;
  calibrationStart = millis();

  Serial.println();

  if (calStage == CAL_IDLE) {

    calStage = CAL_REST;

    Serial.println("STEP 1/3 - REST BASELINE");
    Serial.println("Stay completely relaxed for 5 s.");

  } else if (calStage == CAL_REST) {

    calStage = CAL_MVC;

    Serial.println("STEP 2/3 - MVC");
    Serial.println("Contract maximally and hold 5 s.");

  } else {

    calStage = CAL_VERIFY;

    Serial.println("STEP 3/3 - MVC VERIFY");
    Serial.println("Contract maximally again for 5 s.");
  }
}

void resetCalibration() {

  calStage = CAL_IDLE;

  rest_mV = 0.0;
  mvc_mV = 0.0;

  calSum = 0.0;
  calCount = 0;
  calMax = 0.0;

  Serial.println();
  Serial.println("CALIBRATION RESET - activation back to 0%");
}

void updateCalibration() {

  if (calStage == CAL_IDLE) return;

  // Rest is averaged over the window; MVC takes the peak window.
  if (calStage == CAL_REST) {
    calSum += rms_mV;
    calCount++;
  } else {
    if (rms_mV > calMax) calMax = rms_mV;
  }

  if (millis() - calibrationStart < CAL_DURATION_MS) return;

  if (calStage == CAL_REST) {

    rest_mV = (calCount > 0) ? (calSum / calCount) : 0.0;
    calStage = CAL_IDLE;

    Serial.println();
    Serial.print("REST BASELINE: ");
    Serial.print(rest_mV, 3);
    Serial.println(" mV");
    Serial.println("Press C for step 2 (MVC).");

  } else if (calStage == CAL_MVC) {

    mvc_mV = calMax;
    calStage = CAL_IDLE;

    Serial.println();
    Serial.print("MVC RMS: ");
    Serial.print(mvc_mV, 3);
    Serial.println(" mV");
    Serial.println("Press C for step 3 (verify).");

  } else {

    bool improved = (calMax > mvc_mV);

    if (improved) mvc_mV = calMax;

    calStage = CAL_IDLE;

    Serial.println();
    Serial.print("VERIFY RMS: ");
    Serial.print(calMax, 3);
    Serial.print(" mV  ->  ");
    Serial.print(improved ? "kept" : "kept previous best");
    Serial.print(": ");
    Serial.print(mvc_mV, 3);
    Serial.println(" mV");

    Serial.print("Ratio MVC/rest: ");
    if (rest_mV > 0.001) {
      Serial.println(mvc_mV / rest_mV, 1);
    } else {
      Serial.println("n/a (no baseline)");
    }
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
      advanceCalibration();
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
// RMS AND ACTIVATION
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

  bool calibrating = (calStage != CAL_IDLE);

  // Activation with the rest baseline removed in quadrature:
  //   signal = sqrt(rms^2 - rest^2)
  //   range  = sqrt(mvc^2 - rest^2)
  float signal = rms_mV * rms_mV - rest_mV * rest_mV;
  if (signal < 0.0f) signal = 0.0f;
  signal = sqrt(signal);

  float range = mvc_mV * mvc_mV - rest_mV * rest_mV;

  float activation = 0.0f;

  if (range > 1e-6f) {
    activation = (signal / sqrt(range)) * 100.0f;
    if (activation < 0.0f) activation = 0.0f;
  }

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

  if (calibrating) {
    if (calStage == CAL_REST) Serial.print(" | REST");
    else if (calStage == CAL_MVC) Serial.print(" | MVC");
    else Serial.print(" | VERIFY");
  }

  Serial.println();

  // ---- BLE ----
  // mean,rms,activation,calibrating,batt_mV,batt_pct,charging,flags,rest_mV,mvc_mV
  char line[80];

  snprintf(
      line,
      sizeof(line),
      "%.0f,%.2f,%.1f,%d,%.0f,%d,%d,%d,%.2f,%.2f\n",
      mean_mV,
      rms_mV,
      activation,
      calibrating ? 1 : 0,
      (batt_pct >= 0) ? batt_mV_smooth : 0.0f,
      batt_pct,
      charging ? 1 : 0,
      clipped ? 1 : 0,
      rest_mV,
      mvc_mV
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
  Serial.println("C -> press 1: rest, 2: MVC, 3: verify");
  Serial.println("R -> reset calibration");
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
      advanceCalibration();
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
