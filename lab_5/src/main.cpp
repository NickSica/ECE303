#include <Arduino.h>
#include <string.h>
#include <stdio.h>

int led = 13;
int start_run = 0;
int duty_cycle = 5;

void setup() 
{
    pinMode(led, OUTPUT);
    pinMode(A0, INPUT);
    pinMode(A1, INPUT);
    analogWrite(led, LOW);    
    Serial.begin(9600);
}

void loop() 
{
    if(Serial.available() > 0)
    {
        String ser = Serial.readString();
        start_run = 1;
        if(Serial.readString() == "start")
        {
            start_run = 1;
            analogWrite(led, duty_cycle);
            duty_cycle += 5;
        }
    }
    
    if(start_run && duty_cycle <= 100)
    {
        delay(3000);
        Serial.println("Duty Cycle, LED Resistor Voltage, Photocell Resistor Voltage");
        Serial.println(duty_cycle);

        int led_resistor_value = analogRead(A0);
        float led_resistor_voltage = (float)led_resistor_value * (5.0 / 1023.0);
        Serial.println(led_resistor_voltage);

        int photo_resistor_value = analogRead(A1);
        float photo_resistor_voltage = (float)photo_resistor_value * (5.0 / 1023.0);
        Serial.println(photo_resistor_voltage);
        Serial.println();
        duty_cycle += 5;
        analogWrite(led, 255 * ((float)duty_cycle / 100.0));
    }
    else if(start_run)
    {
        Serial.println("done");
        duty_cycle = 0;
        start_run = 0;
    }
}