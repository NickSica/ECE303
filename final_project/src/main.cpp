#include <Arduino.h>
#include <string.h>

const int fwd = 6;
const int back = 5;
const int trig_pin = 11;
const int echo_pin = 12;
const int led_slow = 10;
const int led_medium = 9;
const int led_fast = 8;

long duration;
long distance;
int start_run = 0;
int duty_cycle = 0;

void ultrasonicControl();
void motorControl();

void setup() 
{
    // Motor Setup
    pinMode(fwd, OUTPUT);
    pinMode(back, OUTPUT);
    
    // Ultrasonic Setup
    pinMode(trig_pin, OUTPUT);
    pinMode(echo_pin, INPUT);

    Serial.begin(9600);
}

void loop() 
{
    ultrasonicControl();
    motorControl();
    delay(250);
}

void motorControl()
{
    // From 10cm to 110cm
    int speed = map(constrain(distance, 10, 100), 10, 100, 0, 255);
    analogWrite(fwd, speed);
    analogWrite(back, 0);
    Serial.print("speed:");
    Serial.println(speed);
}

void ultrasonicControl()
{
    // Trigger sensor
    digitalWrite(trig_pin, LOW);
    delayMicroseconds(5);
    digitalWrite(trig_pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig_pin, LOW);

    // Read duration and get distance
    duration = pulseIn(echo_pin, HIGH);
    distance = (duration / 2.0) / 29.1;

    Serial.print("distance:");
    Serial.println(distance);
}