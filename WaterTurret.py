#!/usr/bin/python3
from time import sleep
from serial import Serial
import struct

'''
 Arduino command

 [start char  (byte b'>')][command] (byte)][ value (2 HEX ASCII)][ check sum (2 HEX ASCII)][new line ('\n')]

 command :

    X , Y ->  set position X or Y  in degree  (90 degree = center)
    P     ->  Start PUMP   0=off  else ON
    D     ->  Disable servoe & pump

    ex:
        b'>Y5A0D\n'     Set servo Y at 90 degree 
        b'>P01EF\n'     start pump
        b'>D00E2\n'     disable pump and servo


'''



class WaterTurret:

  # declaration de l'objet connection au port serie
  HexBYTE = [ b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7',
              b'8', b'9', b'A', b'B', b'C', b'D', b'E', b'F']

  def __init__(self,Port="/dev/ttyUSB0",Baudrate=9600, Timeout= 0.01):
     self.serial = Serial(Port,baudrate=Baudrate,timeout=Timeout)
     self.serial.setDTR(1)
     self.TX_DELAY_TIME = 0.01
     self.minX=0
     self.minY=55
     self.maxX=180
     self.maxY=115
     self.offsetX = 0
     self.offsetY = -5

  # envoi du packet  ajout du header et du checksum
  def sendPacket(self,packet):
     sum = 0
     for item in packet:
        sum = sum + item

     fullPacket = packet + self.HexBYTE[ (sum >> 4) & 0xf] + self.HexBYTE[ sum & 0xf] + b'\n'
     self.serial.write(fullPacket)
#     print(fullPacket)
     sleep(self.TX_DELAY_TIME)

  def servo(self, ID , Degree,Min,Max,Offset):
     Degree = Degree + Offset
     if Degree > Max :
       Degree = Max
     if Degree < Min:
       Degree = Min
     self.sendPacket(b'>'+ID+self.HexBYTE[(Degree>>4) & 0xf]+self.HexBYTE[Degree & 0xf])

  def x(self,Degree):
     self.servo(b'X',Degree,self.minX,self.maxX,self.offsetX)

  def y(self,Degree):
     self.servo(b'Y',Degree,self.minY,self.maxY,self.offsetY)

  def xy(self,DegreeX,DegreeY):
     if not (DegreeX is None):
        self.x(DegreeX)
     if not (DegreeY is None):
        self.y(DegreeY)


  def pump(self,value):
     self.sendPacket(b'>P'+ self.HexBYTE[(value>>4) & 0xf] + self.HexBYTE[value & 0xf])

  def off(self):
     self.sendPacket(b">D00")



if __name__ == '__main__':
   m1 = WaterTurret(Port="/dev/rfcomm1")
   m1.setY(90)
   sleep(1)
   m1.setY(80)
   sleep(1)
   m1.setY(70)
   sleep(1)
   m1.off()

 
