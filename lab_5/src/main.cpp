#include <Arduino.h>
#include <string.h>

int led = 13;
int start_run = 0;
int duty_cycle = 0;

float calcValue(const uint8_t port);

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
            duty_cycle += 1;
        }
    }
    
    if(start_run && duty_cycle < 100)
    {
        float led_resistor_voltage = calcValue(A0) * (5.0 / 1023.0);
        float photo_resistor_voltage = calcValue(A1) * (5.0 / 1023.0);
    
        Serial.println("Duty Cycle, LED Resistor Voltage, Photocell Resistor Voltage");
        Serial.println(duty_cycle);
        Serial.println(led_resistor_voltage);
        Serial.println(photo_resistor_voltage);
        Serial.println();

        duty_cycle += 1;
        analogWrite(led, 255 * ((float)duty_cycle / 100.0));
    }
    else if(start_run)
    {
        Serial.println("done");
        duty_cycle = 0;
        start_run = 0;
    }
}

float calcValue(const uint8_t port)
{
    int good_vals[5];
    int values[5];
    double avg_val = 0;
    // Get values and find avg
    for(int i = 0; i < 5; i++)
    {
        delay(500);
        int val = analogRead(port);
        values[i] = val;
        avg_val += (double)val / 5.0;
    }
    
    // Calculate standard deviation
    double std_dev = 0;
    for(int i = 0; i < 5; i++)
        std_dev += pow(values[i] - avg_val, 2);
    std_dev = sqrt(std_dev / 5.0);

    int good_vals_idx = 0;
    for(int i = 0; i < 5; i++)
    {
        if((values[i] < avg_val + 2*std_dev) || (values[i] > avg_val - 2*std_dev))
        {
            good_vals[good_vals_idx] = values[i];
            good_vals_idx++;
        }
    }

    float final_value = 0;
    for(int i = 0; i < good_vals_idx; i++)
        final_value += (float)good_vals[i];
    
    if(good_vals_idx == 0) 
        final_value = 0;
    else
        final_value /= (float)good_vals_idx;
    
    return final_value; 
}