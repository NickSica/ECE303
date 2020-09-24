#include <Arduino.h>

int led = 13;
int intensity = 0;

void setup() 
{
    pinMode(led, OUTPUT);
    analogWrite(led, LOW);
    Serial.begin(9600);
}

void loop() 
{
    if(Serial.available() > 0)
    {
        Serial.print("Please enter a number from 0 to 255: ");
        intensity = Serial.parseInt();
        Serial.print("\nGot number: ");
        Serial.println(intensity, DEC);
        analogWrite(led, intensity);
    }
}