#include <Arduino.h>
#include <DHT.h>
#include <LiquidCrystal.h>

#define DHTPIN 10
#define DHTTYPE DHT22 


DHT dht(10, DHT22); //creates new instance of dht class on pin 8
//Pin Definitions
const int CR1 = 2;
const int CR2 = 3;
const int CR3 = 4;
const int CR4 = 5;
const int CR5 = 6;
const int CR6 = 7;
const int CR7 = 8;
const int CR8 = 9;
const int PhotoResistor = A0;
int incomingByte = 0;
int incrementor = 0;
//other definitions
int serialTimeout = 3000;
int byteStorage1;

void setup() {
  Serial.begin(9600); //set serial buad rate
  dht.begin();        //initialize serial
  pinMode(CR1, OUTPUT); 
  pinMode(CR2, OUTPUT); 
  pinMode(CR3, OUTPUT); 
  pinMode(CR4, OUTPUT); 
  pinMode(CR5, OUTPUT); 
  pinMode(CR6, OUTPUT); 
  pinMode(CR7, OUTPUT); 
  pinMode(CR8, OUTPUT);  
  pinMode(13, OUTPUT);
  digitalWrite(CR1, HIGH);
  digitalWrite(CR2, HIGH);
  digitalWrite(CR3, HIGH);
  digitalWrite(CR4, HIGH);
  digitalWrite(CR5, HIGH);
  digitalWrite(CR6, HIGH);
  digitalWrite(CR7, HIGH);
  digitalWrite(CR8, HIGH);
}


void updateRelay(char relayNum, char relayState) {
  switch (relayNum)
  {
  case '1':
    if (relayState == '1') {digitalWrite(CR1, LOW);}
    else {digitalWrite(CR1, HIGH);}
    break;
    
    case '2':
    if (relayState == '1') {digitalWrite(CR2, LOW);}
    else {digitalWrite(CR2, HIGH);}
    break;
    
    case '3':
    if (relayState == '1') {digitalWrite(CR3, LOW);}
    else {digitalWrite(CR3, HIGH);}
    break;

    case '4':
    if (relayState == '1') {digitalWrite(CR4, LOW);}
    else {digitalWrite(CR4, HIGH);}
    break;
    
    case '5':
    if (relayState == '1') {digitalWrite(CR5, LOW);}
    else {digitalWrite(CR5, HIGH);}
    break;

    case '6':
    if (relayState == '1') {digitalWrite(CR6, LOW);}
    else {digitalWrite(CR6, HIGH);}
    break;

    case '7':
    if (relayState == '1') {digitalWrite(CR7, LOW);}
    else {digitalWrite(CR7, HIGH);}
    break;
    
    case '8':
    if (relayState == '1') {digitalWrite(CR8, LOW);}
    else {digitalWrite(CR8, HIGH);}
    break;

    case '9':
    enableALL();
    break;
        
    case '10':
    disableALL();
    break;

    default:
    Serial.println("invalid parameter");
    break;
  }
  

}

void disableALL() {
  digitalWrite(CR1, HIGH);
  digitalWrite(CR2, HIGH);
  digitalWrite(CR3, HIGH);
  digitalWrite(CR4, HIGH);
  digitalWrite(CR5, HIGH);
  digitalWrite(CR6, HIGH);
  digitalWrite(CR7, HIGH);
  digitalWrite(CR8, HIGH);
}

void enableALL() {
  digitalWrite(CR1, LOW);
  digitalWrite(CR2, LOW);
  digitalWrite(CR3, LOW);
  digitalWrite(CR4, LOW);
  digitalWrite(CR5, LOW);
  digitalWrite(CR6, LOW);
  digitalWrite(CR7, LOW);
  digitalWrite(CR8, LOW);
}

//main loop 
void loop() {

  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n'); //extrapolte string from data in buffer
    command.trim(); //remove escape sequence and trailing junk
    
    if (command.length() == 2) {            //split string into two segments.
      char relayNum = command.charAt(0);
      char relayState = command.charAt(1);

      updateRelay(relayNum, relayState); //update relay state

      //returns acknoledgement of success or failure to python.
      Serial.print("Success:");
      Serial.println(command);
    } else {
      Serial.print("ERROR: Invalid command length: ");
      Serial.println(command);
    }
  }
  
  float temperature = dht.readTemperature(true); //temp floating point variable
  //float humidity = dht.readHumidity(); //humidity floating point variable
  int lightValue = analogRead(PhotoResistor); // Read the raw analog value (0-1023)
  
  if (temperature > 60) {
    updateRelay('7', '1');
  } else {
    updateRelay('7', '0');
  }

  if (lightValue < 25) {
    updateRelay('8', '1');
  } else {
    updateRelay('8', '0');
  }
Serial.println(lightValue);
}