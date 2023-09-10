volatile uint32_t PULSEWIDTH[128];
volatile bool HIGHPULSE[128];

volatile uint16_t PULSECOUNTER=0;
volatile uint32_t LASTSPARK;
volatile uint32_t TDC = 0;
volatile uint32_t DWELLTIME = 0;
volatile uint32_t SPARKDURATION = 0;
volatile uint32_t ADVANCE = 0;
volatile uint16_t TIMEROVERFLOWS = 0;
bool TDCFLAG = false;

const byte FUELPRESSPIN = A1;
const byte TEMPPIN = A2;
const byte OILPRESSPIN = A4;
const byte BATTVOLTPIN = A3;

void setup()
{
  Serial.begin(9600);
  while (!Serial);
  noInterrupts ();  // protected code
  // Start a freerunning counter
  TCCR1A = 0; // Timer/Counter Control Register 1A cleared
  TCCR1B = 0; // Timer/Counter Control Register 1B cleared
  TCNT1 = 0;  // Timer Count Register cleared
  TIMSK1 = 0; // Timer Interrupt Mask Register cleared
  TIFR1 |= _BV(ICF1); // Timer Interrupt Flag Register - Input Capture Flag cleared
  TIFR1 |= _BV(TOV1); // Timer Interrupt Flag Register - Timer OVerflow Flag cleared
  TCCR1B = _BV(CS10) | // Timer/Counter Control Register 1B - Counter Select start Timer 1, no prescaler
           _BV(ICES1); // Timer/Counter Control Register 1B - Input Capture Edge Select Rising
  TIMSK1 |= _BV(ICIE1); // // Timer Interrupt Mask Registe enable Input Capture Interrupt
  TIMSK1 |= _BV(TOIE1); // Timer Interrupt Mask Register - Timer Overflow Interrupt Enabled 
  interrupts ();

}

ISR(TIMER1_OVF_vect) 
{
  TIMEROVERFLOWS++;
}

ISR(TIMER1_CAPT_vect) 
{
  static uint32_t risingEdgeTime = 0;
  static uint32_t fallingEdgeTime = 0;
  uint16_t overflows = TIMEROVERFLOWS;

  if ((TIFR1 & _BV(TOV1)) && (ICR1 < 1024)) {
    overflows++;
  }
  if (TCCR1B & _BV(ICES1)) { // Interrupted on Rising Edge
    risingEdgeTime = overflows;
    risingEdgeTime = (risingEdgeTime << 16) | ICR1;
      
    if (risingEdgeTime) {
      if (PULSELOWCOUNTER < 128)  {
        PULSEWIDTH[PULSECOUNTER] = risingEdgeTime - fallingEdgeTime;
        HIGHPULSE[PULSECOUNTER] = false;
        PULSECOUNTER=(PULSECOUNTER+1);
      }
    }
    TCCR1B &= ~_BV(ICES1); // Switch to Falling Edge
  }
  else {  // Interrupted on Falling Edge 
    fallingEdgeTime = overflows;
    fallingEdgeTime = (fallingEdgeTime << 16) | ICR1;     
     if (PULSEHIGHCOUNTER < 128) { 
      PULSEWIDTH[PULSECOUNTER] = fallingEdgeTime - risingEdgeTime;
      HIGHPULSE[PULSECOUNTER] = true;
      PULSECOUNTER=(PULSECOUNTER+1);
    } 
    TCCR1B |= _BV(ICES1); // Switch to Rising Edge
  }  
}

void PrintSensors() 
{
  double fuelPressSig = analogRead(FUELPRESSPIN);
  fuelPressSig = fuelPressSig/90;
  double tempSig = analogRead(TEMPPIN);
  tempSig = tempSig/3.3;
  double oilPressSig = analogRead(OILPRESSPIN);
  double battVoltSig = analogRead(BATTVOLTPIN);
  battVoltSig = battVoltSig/60;

  Serial.print("Time: ");
  Serial.println(micros());

  Serial.print("Fuel: ");
  Serial.println(fuelPressSig); 

  Serial.print("Oil: ");
  Serial.println(oilPressSig);  

  Serial.print("Coolant: ");
  Serial.println(tempSig); 

  Serial.print("Battery: ");
  Serial.println(battVoltSig); 
  Serial.println();
}

void PrintIgnitionTiming(float dwellTime, float sparkDuration, float advanceTime) 
{
    
    dwellTime=dwellTime/16;
    sparkDuration=sparkDuration/16;
    advanceTime=advanceTime/16;

    float period = float(dwellTime + sparkDuration) * 4;
    float frequency = 1e6 / period;
    float rpm = frequency*60;
    if (rpm<0 || rpm>10000) {
      rpm=0;
    }
    float advanceAngle = 360*advanceTime/period;
    float dwellAngle = 360*dwellTime/period;
    Serial.print("Frequency: ");
    Serial.println(frequency, 2);
    Serial.print("Period: ");
    Serial.println(period, 2);
    Serial.print("Spark Duration: ");
    Serial.println(sparkDuration, 2);
    Serial.print("Dwell Time: ");
    Serial.println(dwellTime, 2);
    Serial.print("Dwell Angle: ");
    Serial.println(dwellAngle, 2);
    Serial.print("Advance Time: ");
    Serial.println(advanceTime, 2);
    Serial.print("Advance Angle: ");
    Serial.println(advanceAngle, 2);
    Serial.print("RPM: ");
    Serial.println(rpm, 2);
    Serial.println();  
}

void loop()
{
  int n=0;
  int sparkVals = 0;
  int dwellVals = 0;
  int advanceVals = 0;
  float averageHigh=0.0;
  float averageLow=0.0;
  float averageSpark=0.0;
  float averageDwell=0.0;
  float averageAdvance=0.0;

  noInterrupts ();  // protected code
  if (PULSECOUNTER == 128) {
    for(n=1;n<124;n++) {
      if (HIGHPULSE[n]) {
        if (PULSEWIDTH[n] > 100 ) { // Ignore tdc pulse
          averageDwell = averageDwell + PULSEWIDTH[n];
          dwellVals = dwellValse + 1;
        }
        else {
          averageAdvance = averageAdvance +  PULSEWIDTH[n-1];
          advanceVals = advanceVals + 1;
          averageSpark = averageSpark + PULSEWIDTH(n+3);
          sparkVals = sparkVals + 1;
        }
      }
    }
    SPARKDURATION = averageSpark/sparkVals;
    ADVANCE = averageAdvance/advanceVals;
    DWELLTIME= averageDwell/dwellVals;
    PULSEHIGHCOUNTER = 0;
    PULSELOWCOUNTER = 0;
  }
  interrupts ();
  PrintIgnitionTiming(DWELLTIME, SPARKDURATION, ADVANCE);
  PrintSensors();
  
  delay(100);
}
