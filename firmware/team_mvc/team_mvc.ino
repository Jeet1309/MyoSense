#include <Arduino.h>
#include <math.h>

// ============================================
// TEAM KRESIT - MUSCLE BIOAMP CANDY
// ESP32-S3 N16R8
// SINGLE CHANNEL EMG
// SERIAL MONITOR VERSION
// ============================================

// Hardware configuration
#define EMG_PIN 4

// Sampling configuration
const uint32_t SAMPLE_RATE = 2000;
const uint32_t SAMPLE_INTERVAL_US = 500;

// 100 ms RMS window
const uint16_t WINDOW_SIZE = 200;

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

    activation = constrain(
      activation, 0.0, 100.0
    );
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
  Serial.println(" ESP32-S3 N16R8");
  Serial.println("================================");

  Serial.println("GPIO: 4");
  Serial.println("Sampling Rate: 2000 Hz");
  Serial.println("RMS Window: 100 ms");

  Serial.println("--------------------------------");
  Serial.println("System ready!");
  Serial.println("Send C for MVC calibration.");
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