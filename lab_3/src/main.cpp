#include <Arduino.h>

const int leds[] = {11, 5, 6, 44};
long password;
uint8_t correct_nums = 0b0000;
uint8_t num_tries = 0;
uint16_t starting_freq = 31248;
bool locked_out = false;

void setup() 
{
    noInterrupts();
    for(int i = 0; i < 4; i++)
    {
        pinMode(leds[i], OUTPUT);
        digitalWrite(leds[i], LOW);
    }

    // Setup timer 1 pin 11 channel A
    TCCR1A = 0;
    TCCR1B = 0;
    TIMSK1 = 0;
    TCNT1  = 0;
    OCR1A  = starting_freq;                                    // = (16 * 10^6) / (1024 * 100) - 1
    TCCR1B |= (1 << WGM12);
    TCCR1B |= (1 << CS12) | (0 << CS11) | (1 << CS10); // 1024 prescalar
    TIMSK1 |= (1 << OCIE1A);

    // Setup timer 3 pin 5 channel A
    TCCR3A = 0;
    TCCR3B = 0;
    TIMSK3 = 0;
    TCNT3  = 0;
    OCR3A  = starting_freq;                                    // = (16 * 10^6) / (1024 * 4) - 1
    TCCR3B |= (1 << WGM32);
    TCCR3B |= (1 << CS32) | (0 << CS31) | (1 << CS30); // 1024 prescalar
    TIMSK3 |= (1 << OCIE3A);

    // Setup timer 4 pin 6 channel A
    TCCR4A = 0;
    TCCR4B = 0;
    TIMSK4 = 0;
    TCNT4  = 0;
    OCR4A  = starting_freq;                                    // = (16 * 10^6) / (1024 * 100) - 1
    TCCR4B |= (1 << WGM42);
    TCCR4B |= (1 << CS42) | (0 << CS41) | (1 << CS40); // 1024 prescalar
    TIMSK4 |= (1 << OCIE4A);

    // Setup timer 5 pin 44 channel A
    TCCR5A  = 0;
    TCCR5B  = 0;
    TIMSK5  = 0;
    TCNT5   = 0;
    OCR5A   = starting_freq;                                   // = (16 * 10^6) / (1024 * 1) - 1
    TCCR5B |= (1 << WGM52);
    TCCR5B |= (1 << CS52) | (0 << CS51) | (1 << CS50); // 1024 prescalar
    TIMSK5 |= (1 << OCIE5A);
    
    Serial.begin(9600);
    randomSeed(analogRead(0));
    password = random(10000);
    Serial.print("Password is ");
    Serial.println(password, DEC);
    Serial.println("Please enter guess:");
    interrupts();
}

void loop() 
{
    if(num_tries < 5)
    {
        if(Serial.available() > 0)
        {
            int guess = Serial.parseInt();
            Serial.print("Guess is ");
            Serial.println(guess, DEC);
            int temp_password = password;
            for(int i = 0; i <= 3; ++i)
            {
                if(guess % 10 == temp_password % 10)
                {
                    correct_nums |= 1 << i;
                    switch(i)
                    {
                        case 0: TIMSK1 = 0;
                        case 1: TIMSK3 = 0;
                        case 2: TIMSK4 = 0;
                        case 3: TIMSK5 = 0;
                    }
                    digitalWrite(leds[i], LOW);
                }
                guess = guess / 10;
                temp_password = temp_password / 10;
            }

            TCNT1 = 0;
            TCNT3 = 0;
            TCNT4 = 0;
            TCNT5 = 0;
            OCR1A = OCR1A / 2;
            OCR3A = OCR3A / 2;
            OCR4A = OCR4A / 2;
            OCR5A = OCR5A / 2;
            if(num_tries < 4)
                Serial.println("Please enter guess: ");
            num_tries++;
        }
    }
    else if(!locked_out)
    {
        TIMSK1 = 0;
        TIMSK3 = 0;
        TIMSK4 = 0;
        TIMSK5 = 0;
        Serial.println("Out of tries!");
        for(int i = 0; i < 4; i++)
        {
            if((correct_nums & (1 << i)) == 0b0000)
                digitalWrite(leds[i], HIGH);
        }
            locked_out = true;
    }
    
}

ISR(TIMER1_COMPA_vect)
{
    digitalWrite(leds[0], !digitalRead(leds[0]));
}

ISR(TIMER3_COMPA_vect)
{
    digitalWrite(leds[1], !digitalRead(leds[1]));
}

ISR(TIMER4_COMPA_vect)
{
    digitalWrite(leds[2], !digitalRead(leds[2]));
}

ISR(TIMER5_COMPA_vect)
{
    digitalWrite(leds[3], !digitalRead(leds[3]));
}