#include <Arduino.h>
#include <string.h>
#include <dht.h>
#include <SPI.h>
#include <MFRC522.h>
#include <IRremote.h>
//#include <IRremoteInt.h>
#include <LiquidCrystal.h>

#define FWD_PIN 6
#define BACK_PIN 5
#define TRIG_PIN 31
#define ECHO_PIN 12
#define LED_PIN 7
#define BUZZER_PIN 13
#define MOISTURE_POWER 49
#define MOISTURE_PIN A1
#define DHT11_PIN A0
#define SS_PIN 53
#define RST_PIN 4
#define LCD_PIN 26
#define IR_PIN 22

#define ONE 16724175
#define TWO 16718055
#define THREE 16743045
#define UP 16748655
#define DOWN 16769055

int temp;
int moisture;
dht DHT;

MFRC522 mfrc522(SS_PIN, RST_PIN);

IRrecv irrecv(IR_PIN);
decode_results results;

LiquidCrystal lcd(2, 3, 8, 9, 10, 11);

long duration;
long distance;
int access = 0;
int start_run = 0;
int duty_cycle = 0;
double ctrl_speed = 0;
int led_brightness = 0;

void sendData(const char *, double);
void buzzerControl(int);
void ultrasonicControl();
void motorControl();
int sensorControl();
int rfidControl();
void irControl();
void lcdControl();

void setup() 
{
    // Motor Setup
    pinMode(FWD_PIN, OUTPUT);
    pinMode(BACK_PIN, OUTPUT);
    
    // Ultrasonic Setup
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    // Buzzer and LED Setup
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);

    //Moisture Sensor Setup
    pinMode(MOISTURE_POWER, OUTPUT);
    digitalWrite(MOISTURE_POWER, LOW);

    // LCD Setup
    pinMode(LCD_PIN, OUTPUT);
    analogWrite(LCD_PIN, 120);
    lcd.begin(16, 2);
    lcd.on();

    Serial.begin(9600);

    // IR Setup
    irrecv.enableIRIn();

    // RFID Setup
    SPI.begin();
    mfrc522.PCD_Init();
    Serial.println("Approximate your card to the reader...");
    Serial.println();
}

void loop() 
{
    access = rfidControl();
    if((access == 1) && sensorControl())
    {
        ultrasonicControl();
        irControl();
        motorControl();
        sensorControl();
        lcdControl();
    }
    else
    {
        sendData("speed", 0);
        analogWrite(FWD_PIN, 0);
        analogWrite(BACK_PIN, 0);
    }
    
    delay(250);
}

void sendData(const char *setting, double data)
{
    Serial.print(setting);
    Serial.print(":");
    Serial.println(data);
}

void buzzerControl(int freq)
{
    for(int i = 0; i < 100; ++i)
    {
        digitalWrite(BUZZER_PIN, HIGH);
        delay(freq);
        digitalWrite(BUZZER_PIN, LOW);
        delay(freq);
    }
}

void motorControl()
{
    // From 10cm to 110cm
    double speed_out;
    double speed = map(constrain(distance, 10, 100), 10, 100, 0, 255);
    if(ctrl_speed < speed)
        speed_out = ctrl_speed;
    else
        speed_out = speed;
    
    analogWrite(FWD_PIN, speed_out);
    analogWrite(BACK_PIN, 0);
    sendData("speed", speed_out);
}

void ultrasonicControl()
{
    // Trigger sensor
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(5);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Read duration and get distance
    duration = pulseIn(ECHO_PIN, HIGH);
    distance = (duration / 2.0) / 29.1;

    sendData("distance", distance);
}

int sensorControl()
{
    digitalWrite(MOISTURE_POWER, HIGH);
	delay(10);
	moisture = analogRead(MOISTURE_PIN);
	digitalWrite(MOISTURE_POWER, LOW);
    sendData("coolant", moisture);

    DHT.read11(DHT11_PIN);
    temp = DHT.temperature;
    sendData("temp", temp);
    return temp < 36 && moisture > 100;
}

int rfidControl()
{
    // Look for new cards
    if(!mfrc522.PICC_IsNewCardPresent())
        return access;

    // Select one of the cards
    if(!mfrc522.PICC_ReadCardSerial())
        return access;

    //Show UID on serial monitor
    Serial.print("UID tag :");
    String content= "";
    //byte letter;
    for(byte i = 0; i < mfrc522.uid.size; i++)
    {
        Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
        Serial.print(mfrc522.uid.uidByte[i], HEX);
        content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
        content.concat(String(mfrc522.uid.uidByte[i], HEX));
    }

    Serial.println();
    Serial.print("Message : ");
    content.toUpperCase();
    if(content.substring(1) == "AA F1 8D 81")
    {
        buzzerControl(1);
        Serial.println("Access granted");
        Serial.println();
        sendData("access", 1);
        delay(3000);
        return 1;
    }
    else
    {
        buzzerControl(4);
        Serial.println("Access denied");
        sendData("access", 0);
        delay(3000);
        return 0;
    }    
}

void irControl()
{
    if(irrecv.decode(&results))
    {
        sendData("IR_DATA", results.value);
        switch(results.value)
        {
            case ONE:
                led_brightness = 0;
                break;
            case TWO:
                led_brightness = 127;
                break;
            case THREE:
                led_brightness = 255;
                break;
            case UP:
                if(ctrl_speed <= 229.5)
                    ctrl_speed += 25.5;
                break;
            case DOWN:
                if(ctrl_speed >= 25.5)
                    ctrl_speed -= 25.5;
                break;
        }
        analogWrite(LED_PIN, led_brightness);
        sendData("headlight", led_brightness);
        irrecv.resume();
    }
}

void lcdControl()
{
    char buf[6];
    lcd.setCursor(0, 0);
    lcd.write("Speed:");
    int speed = (int)(ctrl_speed / 255 * 100);
    sprintf(buf, "%d", speed);
    lcd.setCursor(6, 0);
    lcd.write(buf);
    lcd.setCursor(0, 1);
    sprintf(buf, "%d", moisture);
    lcd.write(buf);
    lcd.setCursor(4, 1);
    sprintf(buf, "%d", temp);
    lcd.write(buf);
}