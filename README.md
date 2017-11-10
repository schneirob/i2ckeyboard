# i2ckeyboard

This is a proof of principle project, demonstrating the transmission of keyboard
key events via i2c from a Raspberry Pi to an Arduino Micro. The key events are
then recreated on the HID interface of the Arduino Micro.

This project is published as a reference project. It is not to be considered
"ready to use", but may hold valuable hints for others trying to do similar
things. Have fun!

## Setup

![Breadboard setup of Raspberry Pi and Arduino Micro](/img/i2ckeyboard-setup.jpg)

## Requirements

Today is Friday, November 10 2017

* Arduino Micro, Arduino API 1.8.5
  * HID-Project 2.4.4
  * Wire 1.0.0
* Raspberry Pi 3 B, Raspian 2017-09-07-raspbian-stretch-lite.img
  * Python 3.5.3
    * time
    * sys
    * argparse
    * smbus 3.1.2-3
    * asyncio 3.4.3
    * evdev 0.7.0

## i2c communication protocol

data transport protocol to transport key press and release information via i2c
bus with checksums and error detection

7|6|5|4|3|2|1|0
-|-|-|-|-|-|-|-
MSB|||||||LSB

__KEY-ID - Byte__
* 0-7: 8 Bit unsignet int key id to be transmitted via the USB keyboard
  
__ACTION - Byte__
* 0-3: Checksum summing all bits = 1 of the KEY-ID(0-7) and ACTION(4-7)
* 4-5: Key action to be performed
  * 00  Transmission test, no action on ext. keyboard. Set LED status and receive status
  * 01  Press Key
  * 10  Release Key
  * 11  Release all
* 6: Set connect LED (0 turn LED off, 1 turn LED on)
* 7: uneven bit - force number of bits = 1 to be uneven (KEY-ID(0-7) + ACTION(4-7))
    
__CONFIRM - Byte__
* 0-3: Checksum summing all bits = 1 of the KEY-ID(0-7) and the ACTION(0-7)
* 4: Status of connect LED
* 5: Status of hardware switch
* 6: checksum / execution error (0: no error, 1: error)
* 7: uneven bit - force number of bits = 1 of confirm byte to be uneven

## Acknowledgement

Special thanks goes out to @NicoHood
[http://www.nicohood.de](http://www.nicohood.de) for his great HID-Project and
@donid for his [akuhell](https://github.com/donid/akuhell) insight into arduino
keyboard keylayout translation. After two weeks of continuous spare time work
on getting German keyboard layout work, stumbling upon akuhell opened some eyes.

Another special thanks goes out to Oscar Liang for his extensive article on
[Raspberry Pi and Arduino Connected Using
I2C](https://oscarliang.com/raspberry-pi-arduino-connected-i2c/). The
explanation saved the Raspberry Pi input ports from beeing fried. This is a
recommendet reading for anyone connecting a Pi and an Arduino via i2c/TWI.

Thanks to all Open Source and Open Hardware providers that allow me to play 
around on this high meta level of creating new applications!
