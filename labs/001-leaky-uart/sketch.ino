// ============================================================
// ChipsvsCrackerZ — Lab 001: Leaky UART
// Difficulty: Easy | Points: 250
// ============================================================
// SCENARIO:
// A prototype IoT smart-lock controller is leaking debug info
// over its UART TX line. The developers forgot to strip their
// debug output before shipping. Tap into the serial bus and
// find the hardcoded master credential hidden in the boot
// sequence.
//
// OBJECTIVE:
// Read the serial monitor output carefully. The flag is
// printed during the device boot sequence.
// ============================================================

const int LED_STATUS  = 2;   // Onboard blue LED (GPIO2)
const int LED_RED     = 4;   // Red LED — error / locked
const int LED_GREEN   = 5;   // Green LED — unlocked

const int BAUD_RATE   = 115200;

// Simulated EEPROM credentials (the "leak")
const char* MASTER_KEY = "d34d_b33f_c0ff33";

void bootSequence() {
  Serial.println("========================================");
  Serial.println("  SmartLock Pro v2.1.7 — Boot Sequence  ");
  Serial.println("========================================");
  delay(800);

  Serial.println("[  OK  ] Initializing MCU core...");
  delay(400);

  Serial.println("[  OK  ] Clock source: XTAL 40MHz");
  delay(300);

  Serial.println("[  OK  ] GPIO subsystem ready");
  delay(200);

  Serial.println("[  OK  ] UART0 initialized @ 115200 baud");
  delay(400);

  Serial.println("[  OK  ] Loading EEPROM configuration...");
  delay(600);

  // ---- THE LEAK ----
  Serial.println("[ DBG  ] EEPROM dump @ 0x3F400000:");
  Serial.print("[ DBG  ]   MASTER_KEY = ");
  Serial.println(MASTER_KEY);
  Serial.print("[ DBG  ]   AUTH_TOKEN = FLAG{");
  Serial.print(MASTER_KEY);
  Serial.println("}");
  Serial.println("[ DBG  ]   LOCK_STATE = 0x00 (LOCKED)");
  // ---- END LEAK ----

  delay(500);

  Serial.println("[  OK  ] Wi-Fi module powered on");
  delay(300);

  Serial.println("[ WARN ] Debug UART logging is ENABLED");
  Serial.println("[ WARN ] Disable before production deployment!");
  delay(400);

  Serial.println("[  OK  ] BLE advertising started");
  delay(200);

  Serial.println("[  OK  ] Servo motor calibrated — 0 deg (LOCKED)");
  delay(300);

  Serial.println("========================================");
  Serial.println("  SmartLock Pro — Ready. Waiting for    ");
  Serial.println("  authorized NFC tag or BLE handshake.  ");
  Serial.println("========================================");
  Serial.println();
}

void setup() {
  Serial.begin(BAUD_RATE);
  
  pinMode(LED_STATUS, OUTPUT);
  pinMode(LED_RED, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);

  // Start in locked state
  digitalWrite(LED_RED, HIGH);
  digitalWrite(LED_GREEN, LOW);

  delay(1000);
  bootSequence();
}

void loop() {
  // Heartbeat blink — device is alive
  digitalWrite(LED_STATUS, HIGH);
  delay(500);
  digitalWrite(LED_STATUS, LOW);
  delay(500);

  // Periodic "status" log (noise to make the user scroll)
  static unsigned long lastLog = 0;
  if (millis() - lastLog > 5000) {
    lastLog = millis();
    Serial.print("[ SYS  ] Uptime: ");
    Serial.print(millis() / 1000);
    Serial.println("s | Lock: ENGAGED | NFC: no tag | BLE: idle");
  }
}
