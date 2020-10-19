#include <Arduino.h>

int led = 6;

void setup() 
{
    pinMode(led, OUTPUT);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);

    noInterrupts();
    // Setup fast PWM timer 4 channel A pin 6
    TCCR4A = 0;
    TCCR4B = 0;
    TIMSK4 = 0;
    TCNT4  = 0;
    ICR4   = 12500;
    OCR4A  = 625;
    TCCR4A |= (1 << WGM41);
    TCCR4A |= (1 << COM4A1);
    TCCR4B |= (1 << WGM43);
    TCCR4B |= (0 << CS41) | (1 << CS40);
    
    Serial.begin(9600);
    interrupts();
}

void loop() 
{
    if(OCR4A <= 12500)
    {
        delay(2000);
        Serial.println("Duty Cycle, LED Resistor Voltage, Photocell Resistor Voltage");

        int duty_cycle = (int)((float)OCR4A / (float)ICR4 * 100);
        Serial.println(duty_cycle);

        int led_resistor_value = analogRead(A0);
        float led_resistor_voltage = (float)led_resistor_value * (5.0 / 1023.0);
        Serial.println(led_resistor_voltage);

        int photo_resistor_value = analogRead(A1);
        float photo_resistor_voltage = (float)photo_resistor_value * (5.0 / 1023.0);
        Serial.println(photo_resistor_voltage);
        Serial.println();
        OCR4A += 625;
    }
}