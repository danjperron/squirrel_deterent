# squirrel_deterrent
Squirrel deterrent using water gun turret with AI control 

Presently it only contains the water gun turret with  the Raspberry Pi python class to access the Arduino communication for the turret

it is an Arduino mini pro 8MHz at 3.3v because I'm using the bluetooth HC05 transmitter to access the turret via an Raspberry Pi.


On the raspberry Pi  use  bluettoothclt to pair the device.  

      sudo bluetoothctl
      agent on 
      scan on
      trust xx:xx:xx:xx:xx:xx
      pair  xx:xx:xx:xx:xx:xx
      quit
      
 
 P.S. xx:xx.. represent the HC05 mac address
 
 
After that you need to create an rfcomm device

    sudo rfcomm bind /dev/rfcomm1 xx:xx:xx:xx:xx:xx 1

And now you are ready to connect via serial using /dev/rfcomm1


calibrateTurret is an application to create a grid to convert screen position to  turret x,y angle positio
turretPoint  is the module to contains all points. 
plane3Points  is the surface module to find best fit point conversion from screen position to  xy angle
Poiny         is the module to convert x and y point
WaterTurret   is the module to directly control the turret via /dev/rfcomm



To drive the  windshield washer pump I'm using a 3Dprinter bed heater controller. I change the resistor on the opto to enable 3.3V output. From 10K to 1K.



