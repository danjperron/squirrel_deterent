/*

  Servo communication


  command  

  [start character '>'][command][ 2 character (1byte) hex value][2 characters (1byte) hex check sum][new line]

  command: 
           X -> servo X  value :   angle 0 to 180 degree
           Y -> servo Y  value : 
           P -> pump      value :  0=off  !0 ON
           D -> Disable X&Y servo; (shutoff) value could be anything
           ex:  >X5A00\n  servoX at 80 degree
           
  
  Serial Event example

  When new serial data arrives, this sketch adds it to a String.
  When a newline is received, the loop prints the string and clears it.

  A good test for this is to try it with a GPS receiver that sends out
  NMEA 0183 sentences.

  NOTE: The serialEvent() feature is not available on the Leonardo, Micro, or
  other ATmega32U4 based boards.

  created 9 May 2011
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/SerialEvent
*/

#include <Servo.h>
#define START_BYTE '>'


#define PIN_SERVO_X 5
#define PIN_SERVO_Y 6
#define PIN_PUMP    7

class myServo: Servo
{
   public:
      bool ServoEnable;
      byte Pin;
      
      myServo(byte _pin)
     {
       Pin = _pin;
       ServoEnable=false;
     }

     virtual void write(int  _timing)
     {
        if(!ServoEnable)
          attach(Pin);
          if(_timing <0)
             _timing=0;
          if(_timing >180)
             _timing=180;
          Servo::write(_timing);
          ServoEnable=true;
     }

     void turnOff()
     {
        if(ServoEnable)
         {
            Servo::detach();
            ServoEnable=false;
         }
     }
  
};


myServo servoX(PIN_SERVO_X);
myServo servoY(PIN_SERVO_Y);

#define BUFFER_SIZE 32
int  rcv_buffer_ptr;
char rcv_buffer[BUFFER_SIZE];

#define RCV_WAIT_START 0
#define RCV_GET_STRING 1
#define RCV_GOT_STRING 2

volatile byte rcv_stat=RCV_WAIT_START;
 
void setup() {
  // initialize serial:
  Serial.begin(9600);
  rcv_buffer_ptr=0;
  
  pinMode(PIN_PUMP, OUTPUT);
  digitalWrite(PIN_PUMP, LOW);
}



void decodeInputString()
{
  int loop;
  byte count;
  int sum = '>';
  char command;
  int value,cksum;


  if(rcv_buffer_ptr!=5)
     return;

  count= sscanf(rcv_buffer,"%c%02X%02X",&command,&value,&cksum);

  if(count!=3) 
    {
//      Serial.print("count");
//      Serial.println(count);
      return;
    }
  
  for(loop=0;loop<3;loop++)
    sum+= (int) rcv_buffer[loop];

  sum &= 0xff;

  /*Serial.print("Command");
  Serial.println(command);
  Serial.print("Value:");
  Serial.println(value);
  Serial.print("cksum:");
  Serial.println(cksum); 
  Serial.print("calc cksum:");
  Serial.println(sum & 0xff);
  */

  if(sum != cksum)
     return;

  if(command == 'X')
      servoX.write(value);
  else if(command == 'Y')
      servoY.write(value);
  else if(command == 'P')
     digitalWrite(PIN_PUMP, value);
  else if(command == 'D')
     {
        servoX.turnOff();
        servoY.turnOff();
        digitalWrite(PIN_PUMP,0);
     }
}




void loop() {
 
  if(rcv_stat == RCV_GOT_STRING)
  {
    decodeInputString();
    rcv_stat = RCV_WAIT_START;
  }

  
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // do we have the start character
    if(rcv_stat == RCV_WAIT_START)
       {
          if(inChar == START_BYTE)
           {
             rcv_stat=RCV_GET_STRING;
             rcv_buffer[0]=0;
             rcv_buffer_ptr=0;
           }
       }
     else if(rcv_stat == RCV_GET_STRING)
     {
        if(inChar == '\n')
           rcv_stat = RCV_GOT_STRING;
         else
         {
         rcv_buffer[rcv_buffer_ptr++]=inChar;
         if(rcv_buffer_ptr >=  BUFFER_SIZE)
           {
              rcv_buffer_ptr=0;
              rcv_stat = RCV_WAIT_START;
           }
           else
           rcv_buffer[rcv_buffer_ptr]=0;
         }
              
     }
  }
}
