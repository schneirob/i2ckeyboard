/*
 * i2ckeyboard
 * Transport key press and release information via i2c bus with checksums and error detection
 * 
 *  7  6  5  4  3  2  1  0
 * MSB                  LSB
 * 
 * KEY-ID - Byte:
 *   0-7: 8 Bit unsignet int key id to be transmitted via the USB keyboard
 *        250: special key: releaseAll keys
 *   
 * ACTION - Byte:
 *   0-3: Checksum summing all bits = 1 of the KEY-ID(0-7) and ACTION(4-7)
 *   4-5: Key action to be performed
 *          00  Transmission test, no action on ext. keyboard. Set LED status and receive status
 *          01  Press Key
 *          10  Release Key
 *          11  Release all
 *     6: Set connect LED (0 turn LED off, 1 turn LED on)
 *     7: uneven bit - force number of bits = 1 to be uneven (KEY-ID(0-7) + ACTION(4-7))
 *     
 * CONFIRM - Byte:
 *   0-3: Checksum summing all bits = 1 of the KEY-ID(0-7) and the ACTION(0-7)
 *     4: Status of connect LED
 *     5: Status of hardware switch
 *     6: checksum / execution error (0: no error, 1: error)
 *     7: uneven bit - force number of bits = 1 of confirm byte to be uneven
 *     
 */

#include <Wire.h>  // do manually: globally disable digitalWrite(SDA, 1) 
                   // and digitalWrite(SCL, 1) to prevent 5V glitches 
		   // on 3.3V I2C Bus

#include "HID-Project.h"

#define SLAVE_ADDRESS 0x10

const byte CONNECT_LED = 13; // 13: Arduino Micro onboard LED
const byte HARDWARE_SWITCH = 4;
const byte DEVICE_ID = 0b10000010; // when reading befor sending, return this ID

byte keyid = 0;
byte action = 0;

boolean status_hardware_switch = false;
boolean nothing_received_since_restart = true;

/*
 * bitSum
 * Calculate the number of bits = 1 in the given data byte
 * 
 * data: byte of data to count number of bits = 1
 * returns: number of bits = 1
 */
byte bitSum(byte data) {
  byte result = 0;
  for(int n = 0; n < 8; n++) {
    result += bitRead(data, n);
  }
  return result;
}

/*
 * check
 * calculate and check checksums; generate confirmation byte
 * return: confirmation byte
 */
byte check() {
  // checkinput: sum of bits keyid(0-7) and action (4-7)
  byte checkinput = bitSum(keyid) + bitSum(action & 0b11110000);

  // to confirm the data the checksum (sum of bits) of keyid(0-7) and action(0-7) is calculated
  byte confirmsum = bitSum(keyid) + bitSum(action);

  // look for transmission errors by checking checkinput sum of bits and 
  // confirming that number of bits = 1 is uneven
  if(checkinput != (action & 0b00001111)) {
    bitSet(confirmsum, 6);
  } 
  else if(bitRead(checkinput, 0) == 0) {
    bitSet(confirmsum, 6);
  }

  // include status of hardware switch
  if(digitalRead(HARDWARE_SWITCH) == HIGH) {
    bitSet(confirmsum, 5);
  }

  // include status of connect LED
  if(digitalRead(CONNECT_LED) == HIGH) {
    bitSet(confirmsum, 4);
  }

  // set uneven bit
  if(bitRead(bitSum(confirmsum), 0) == 0) {
    bitSet(confirmsum, 7);
  }

  return confirmsum;
}

/*
 * setup
 * setup the base parameters and initialize communication (i2c)
 */
void setup() {

  // initialize i2c as slave
  Wire.begin(SLAVE_ADDRESS);
  digitalWrite(SDA, 0); // we have to prevent internal pull ups beeing active!
  digitalWrite(SCL, 0);
  
  // define callbacks for i2c communication
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  // set connect LED as output and turn connect LED off
  pinMode(CONNECT_LED, OUTPUT);
  digitalWrite(CONNECT_LED, LOW);

  // set hardware switch as input
  pinMode(HARDWARE_SWITCH, INPUT);

  // initialize the Keyboard
  Keyboard.begin();
  
}  

/*
 * loop
 */
void loop() {
  delay(100);
}

/*
 * receiveData
 * callback to receive data via the i2c bus
 * 
 */
void receiveData(int byteCount){
  while(Wire.available()) {
    keyid = action;
    action = Wire.read();
  }
  nothing_received_since_restart = false;
}

/*
 * sedData
 * callback for sending data
 */
void sendData(){
  // if device is freshly connected, send device ID on read
  if(nothing_received_since_restart == true) {
    Wire.write(DEVICE_ID);
    delayMicroseconds(4); // Not waiting causes communication trouble with RPI - sometimes.
    return;
  }

  // if keyid and action = 0, send device ID (recheck device id during operation)
  if(action == 0b00000000 && keyid == 0b00000000) {
    Wire.write(DEVICE_ID);
    delayMicroseconds(4); // Not waiting causes communication trouble with RPI - sometimes.
    return;
  }
  
  byte confirm = check();
  Wire.write(confirm);

  // perform required action on no error
  if(bitRead(confirm, 6) == 0) {
    // Keyboardaction is allways limited by the hardware switch
    if(bitRead(confirm, 5)) {
      if((action & 0b00110000) == 0b00000000) {
        // Transmission test, do not transmit keyboard input
      } else if((action & 0b00110000) == 0b00110000) {
        // Release all
        Keyboard.releaseAll();
      } else if((action & 0b00110000) == 0b00010000) {
        // Press Key
        keytranslate(keyid, true);
      } else if((action & 0b00110000) == 0b00100000) {
        // Release Key
        keytranslate(keyid, false);
     }
   }
    
    // set connect LED
    if(bitRead(action, 6) == 0) {
      digitalWrite(CONNECT_LED, LOW);
    } else {
      digitalWrite(CONNECT_LED, HIGH);
    }

    // we have done all we could, so lets reset keyid and action
    action = 0b00000000;
    keyid = 0b00000000;

  }
   
  delayMicroseconds(4); // Not waiting causes communication trouble with RPI - sometimes.
}

/*
 * keytranslate
 * translate key numbers from evdev events into key presses
 * for the Arduino.
 * id: keyid from evdev event.code
 * press_key: press key on true, release key on false
 */
void keytranslate(byte id, bool press_key) {
  if(id == (byte)1) {
    // KEY_ESC
    if(press_key) {
      Keyboard.press(KEY_ESC);
    } else {
      Keyboard.release(KEY_ESC);
    }
  }
  else if(id == (byte)2) {
    // KEY_1
    if(press_key) {
      Keyboard.press(KEY_1);
    } else {
      Keyboard.release(KEY_1);
    }
  }
  else if(id == (byte)3) {
    // KEY_2
    if(press_key) {
      Keyboard.press(KEY_2);
    } else {
      Keyboard.release(KEY_2);
    }
  }
  else if(id == (byte)4) {
    // KEY_3
    if(press_key) {
      Keyboard.press(KEY_3);
    } else {
      Keyboard.release(KEY_3);
    }
  }
  else if(id == (byte)5) {
    // KEY_4
    if(press_key) {
      Keyboard.press(KEY_4);
    } else {
      Keyboard.release(KEY_4);
    }
  }
  else if(id == (byte)6) {
    // KEY_5
    if(press_key) {
      Keyboard.press(KEY_5);
    } else {
      Keyboard.release(KEY_5);
    }
  }
  else if(id == (byte)7) {
    // KEY_6
    if(press_key) {
      Keyboard.press(KEY_6);
    } else {
      Keyboard.release(KEY_6);
    }
  }
  else if(id == (byte)8) {
    // KEY_7
    if(press_key) {
      Keyboard.press(KEY_7);
    } else {
      Keyboard.release(KEY_7);
    }
  }
  else if(id == (byte)9) {
    // KEY_8
    if(press_key) {
      Keyboard.press(KEY_8);
    } else {
      Keyboard.release(KEY_8);
    }
  }
  else if(id == (byte)10) {
    // KEY_9
    if(press_key) {
      Keyboard.press(KEY_9);
    } else {
      Keyboard.release(KEY_9);
    }
  }
  else if(id == (byte)11) {
    // KEY_0
    if(press_key) {
      Keyboard.press(KEY_0);
    } else {
      Keyboard.release(KEY_0);
    }
  }
  else if(id == (byte)12) {
    // KEY_MINUS
    if(press_key) {
      Keyboard.press(KEY_MINUS);
    } else {
      Keyboard.release(KEY_MINUS);
    }
  }
  else if(id == (byte)13) {
    // KEY_EQUAL
    if(press_key) {
      Keyboard.press(KEY_EQUAL);
    } else {
      Keyboard.release(KEY_EQUAL);
    }
  }
  else if(id == (byte)14) {
    // KEY_BACKSPACE
    if(press_key) {
      Keyboard.press(KEY_BACKSPACE);
    } else {
      Keyboard.release(KEY_BACKSPACE);
    }
  }
  else if(id == (byte)15) {
    // KEY_TAB
    if(press_key) {
      Keyboard.press(KEY_TAB);
    } else {
      Keyboard.release(KEY_TAB);
    }
  }
  else if(id == (byte)16) {
    // KEY_Q
    if(press_key) {
      Keyboard.press(KEY_Q);
    } else {
      Keyboard.release(KEY_Q);
    }
  }
  else if(id == (byte)17) {
    // KEY_W
    if(press_key) {
      Keyboard.press(KEY_W);
    } else {
      Keyboard.release(KEY_W);
    }
  }
  else if(id == (byte)18) {
    // KEY_E
    if(press_key) {
      Keyboard.press(KEY_E);
    } else {
      Keyboard.release(KEY_E);
    }
  }
  else if(id == (byte)19) {
    // KEY_R
    if(press_key) {
      Keyboard.press(KEY_R);
    } else {
      Keyboard.release(KEY_R);
    }
  }
  else if(id == (byte)20) {
    // KEY_T
    if(press_key) {
      Keyboard.press(KEY_T);
    } else {
      Keyboard.release(KEY_T);
    }
  }
  else if(id == (byte)21) {
    // KEY_Y
    if(press_key) {
      Keyboard.press(KEY_Y);
    } else {
      Keyboard.release(KEY_Y);
    }
  }
  else if(id == (byte)22) {
    // KEY_U
    if(press_key) {
      Keyboard.press(KEY_U);
    } else {
      Keyboard.release(KEY_U);
    }
  }
  else if(id == (byte)23) {
    // KEY_I
    if(press_key) {
      Keyboard.press(KEY_I);
    } else {
      Keyboard.release(KEY_I);
    }
  }
  else if(id == (byte)24) {
    // KEY_O
    if(press_key) {
      Keyboard.press(KEY_O);
    } else {
      Keyboard.release(KEY_O);
    }
  }
  else if(id == (byte)25) {
    // KEY_P
    if(press_key) {
      Keyboard.press(KEY_P);
    } else {
      Keyboard.release(KEY_P);
    }
  }
  else if(id == (byte)26) {
    // KEY_LEFTBRACE
    if(press_key) {
      Keyboard.press(KEY_LEFT_BRACE);
    } else {
      Keyboard.release(KEY_LEFT_BRACE);
    }
  }
  else if(id == (byte)27) {
    // KEY_RIGHTBRACE
    if(press_key) {
      Keyboard.press(KEY_RIGHT_BRACE);
    } else {
      Keyboard.release(KEY_RIGHT_BRACE);
    }
  }
  else if(id == (byte)28) {
    // KEY_ENTER
    if(press_key) {
      Keyboard.press(KEY_ENTER);
    } else {
      Keyboard.release(KEY_ENTER);
    }
  }
  else if(id == (byte)29) {
    // KEY_LEFTCTRL
    if(press_key) {
      Keyboard.press(KEY_LEFT_CTRL);
    } else {
      Keyboard.release(KEY_LEFT_CTRL);
    }
  }
  else if(id == (byte)30) {
    // KEY_A
    if(press_key) {
      Keyboard.press(KEY_A);
    } else {
      Keyboard.release(KEY_A);
    }
  }
  else if(id == (byte)31) {
    // KEY_S
    if(press_key) {
      Keyboard.press(KEY_S);
    } else {
      Keyboard.release(KEY_S);
    }
  }
  else if(id == (byte)32) {
    // KEY_D
    if(press_key) {
      Keyboard.press(KEY_D);
    } else {
      Keyboard.release(KEY_D);
    }
  }
  else if(id == (byte)33) {
    // KEY_F
    if(press_key) {
      Keyboard.press(KEY_F);
    } else {
      Keyboard.release(KEY_F);
    }
  }
  else if(id == (byte)34) {
    // KEY_G
    if(press_key) {
      Keyboard.press(KEY_G);
    } else {
      Keyboard.release(KEY_G);
    }
  }
  else if(id == (byte)35) {
    // KEY_H
    if(press_key) {
      Keyboard.press(KEY_H);
    } else {
      Keyboard.release(KEY_H);
    }
  }
  else if(id == (byte)36) {
    // KEY_J
    if(press_key) {
      Keyboard.press(KEY_J);
    } else {
      Keyboard.release(KEY_J);
    }
  }
  else if(id == (byte)37) {
    // KEY_K
    if(press_key) {
      Keyboard.press(KEY_K);
    } else {
      Keyboard.release(KEY_K);
    }
  }
  else if(id == (byte)38) {
    // KEY_L
    if(press_key) {
      Keyboard.press(KEY_L);
    } else {
      Keyboard.release(KEY_L);
    }
  }
  else if(id == (byte)39) {
    // KEY_SEMICOLON
    if(press_key) {
      Keyboard.press(KEY_SEMICOLON);
    } else {
      Keyboard.release(KEY_SEMICOLON);
    }
  }
  else if(id == (byte)40) {
    // KEY_APOSTROPHE
    if(press_key) {
      Keyboard.press(KEY_QUOTE);
    } else {
      Keyboard.release(KEY_QUOTE);
    }
  }
  else if(id == (byte)41) {
    // KEY_GRAVE
    if(press_key) {
      Keyboard.press(KEY_TILDE);
    } else {
      Keyboard.release(KEY_TILDE);
    }
  }
  else if(id == (byte)42) {
    // KEY_LEFTSHIFT
    if(press_key) {
      Keyboard.press(KEY_LEFT_SHIFT);
    } else {
      Keyboard.release(KEY_LEFT_SHIFT);
    }
  }
  else if(id == (byte)43) {
    // KEY_BACKSLASH
    if(press_key) {
      Keyboard.press(KEY_BACKSLASH);
    } else {
      Keyboard.release(KEY_BACKSLASH);
    }
  }
  else if(id == (byte)44) {
    // KEY_Z
    if(press_key) {
      Keyboard.press(KEY_Z);
    } else {
      Keyboard.release(KEY_Z);
    }
  }
  else if(id == (byte)45) {
    // KEY_X
    if(press_key) {
      Keyboard.press(KEY_X);
    } else {
      Keyboard.release(KEY_X);
    }
  }
  else if(id == (byte)46) {
    // KEY_C
    if(press_key) {
      Keyboard.press(KEY_C);
    } else {
      Keyboard.release(KEY_C);
    }
  }
  else if(id == (byte)47) {
    // KEY_V
    if(press_key) {
      Keyboard.press(KEY_V);
    } else {
      Keyboard.release(KEY_V);
    }
  }
  else if(id == (byte)48) {
    // KEY_B
    if(press_key) {
      Keyboard.press(KEY_B);
    } else {
      Keyboard.release(KEY_B);
    }
  }
  else if(id == (byte)49) {
    // KEY_N
    if(press_key) {
      Keyboard.press(KEY_N);
    } else {
      Keyboard.release(KEY_N);
    }
  }
  else if(id == (byte)50) {
    // KEY_M
    if(press_key) {
      Keyboard.press(KEY_M);
    } else {
      Keyboard.release(KEY_M);
    }
  }
  else if(id == (byte)51) {
    // KEY_COMMA
    if(press_key) {
      Keyboard.press(KEY_COMMA);
    } else {
      Keyboard.release(KEY_COMMA);
    }
  }
  else if(id == (byte)52) {
    // KEY_DOT
    if(press_key) {
      Keyboard.press(KEY_PERIOD);
    } else {
      Keyboard.release(KEY_PERIOD);
    }
  }
  else if(id == (byte)53) {
    // KEY_SLASH
    if(press_key) {
      Keyboard.press(KEY_SLASH);
    } else {
      Keyboard.release(KEY_SLASH);
    }
  }
  else if(id == (byte)54) {
    // KEY_RIGHTSHIFT
    if(press_key) {
      Keyboard.press(KEY_RIGHT_SHIFT);
    } else {
      Keyboard.release(KEY_RIGHT_SHIFT);
    }
  }
  else if(id == (byte)55) {
    // KEY_KPASTERISK
    if(press_key) {
      Keyboard.press(KEYPAD_MULTIPLY);
    } else {
      Keyboard.release(KEYPAD_MULTIPLY);
    }
  }
  else if(id == (byte)56) {
    // KEY_LEFTALT
    if(press_key) {
      Keyboard.press(KEY_LEFT_ALT);
    } else {
      Keyboard.release(KEY_LEFT_ALT);
    }
  }
  else if(id == (byte)57) {
    // KEY_SPACE
    if(press_key) {
      Keyboard.press(KEY_SPACE);
    } else {
      Keyboard.release(KEY_SPACE);
    }
  }
  else if(id == (byte)58) {
    // KEY_CAPSLOCK
    if(press_key) {
      Keyboard.press(KEY_CAPS_LOCK);
    } else {
      Keyboard.release(KEY_CAPS_LOCK);
    }
  }
  else if(id == (byte)59) {
    // KEY_F1
    if(press_key) {
      Keyboard.press(KEY_F1);
    } else {
      Keyboard.release(KEY_F1);
    }
  }
  else if(id == (byte)60) {
    // KEY_F2
    if(press_key) {
      Keyboard.press(KEY_F2);
    } else {
      Keyboard.release(KEY_F2);
    }
  }
  else if(id == (byte)61) {
    // KEY_F3
    if(press_key) {
      Keyboard.press(KEY_F3);
    } else {
      Keyboard.release(KEY_F3);
    }
  }
  else if(id == (byte)62) {
    // KEY_F4
    if(press_key) {
      Keyboard.press(KEY_F4);
    } else {
      Keyboard.release(KEY_F4);
    }
  }
  else if(id == (byte)63) {
    // KEY_F5
    if(press_key) {
      Keyboard.press(KEY_F5);
    } else {
      Keyboard.release(KEY_F5);
    }
  }
  else if(id == (byte)64) {
    // KEY_F6
    if(press_key) {
      Keyboard.press(KEY_F6);
    } else {
      Keyboard.release(KEY_F6);
    }
  }
  else if(id == (byte)65) {
    // KEY_F7
    if(press_key) {
      Keyboard.press(KEY_F7);
    } else {
      Keyboard.release(KEY_F7);
    }
  }
  else if(id == (byte)66) {
    // KEY_F8
    if(press_key) {
      Keyboard.press(KEY_F8);
    } else {
      Keyboard.release(KEY_F8);
    }
  }
  else if(id == (byte)67) {
    // KEY_F9
    if(press_key) {
      Keyboard.press(KEY_F9);
    } else {
      Keyboard.release(KEY_F9);
    }
  }
  else if(id == (byte)68) {
    // KEY_F10
    if(press_key) {
      Keyboard.press(KEY_F10);
    } else {
      Keyboard.release(KEY_F10);
    }
  }
  else if(id == (byte)69) {
    // KEY_NUMLOCK
    if(press_key) {
      Keyboard.press(KEY_NUM_LOCK);
    } else {
      Keyboard.release(KEY_NUM_LOCK);
    }
  }
  else if(id == (byte)70) {
    // KEY_SCROLLLOCK
    if(press_key) {
      Keyboard.press(KEY_SCROLL_LOCK);
    } else {
      Keyboard.release(KEY_SCROLL_LOCK);
    }
  }
  else if(id == (byte)71) {
    // KEY_KP7
    if(press_key) {
      Keyboard.press(KEYPAD_7);
    } else {
      Keyboard.release(KEYPAD_7);
    }
  }
  else if(id == (byte)72) {
    // KEY_KP8
    if(press_key) {
      Keyboard.press(KEYPAD_8);
    } else {
      Keyboard.release(KEYPAD_8);
    }
  }
  else if(id == (byte)73) {
    // KEY_KP9
    if(press_key) {
      Keyboard.press(KEYPAD_9);
    } else {
      Keyboard.release(KEYPAD_9);
    }
  }
  else if(id == (byte)74) {
    // KEY_KPMINUS
    if(press_key) {
      Keyboard.press(KEYPAD_SUBTRACT);
    } else {
      Keyboard.release(KEYPAD_SUBTRACT);
    }
  }
  else if(id == (byte)75) {
    // KEY_KP4
    if(press_key) {
      Keyboard.press(KEYPAD_4);
    } else {
      Keyboard.release(KEYPAD_4);
    }
  }
  else if(id == (byte)76) {
    // KEY_KP5
    if(press_key) {
      Keyboard.press(KEYPAD_5);
    } else {
      Keyboard.release(KEYPAD_5);
    }
  }
  else if(id == (byte)77) {
    // KEY_KP6
    if(press_key) {
      Keyboard.press(KEYPAD_6);
    } else {
      Keyboard.release(KEYPAD_6);
    }
  }
  else if(id == (byte)78) {
    // KEY_KPPLUS
    if(press_key) {
      Keyboard.press(KEYPAD_ADD);
    } else {
      Keyboard.release(KEYPAD_ADD);
    }
  }
  else if(id == (byte)79) {
    // KEY_KP1
    if(press_key) {
      Keyboard.press(KEYPAD_1);
    } else {
      Keyboard.release(KEYPAD_1);
    }
  }
  else if(id == (byte)80) {
    // KEY_KP2
    if(press_key) {
      Keyboard.press(KEYPAD_2);
    } else {
      Keyboard.release(KEYPAD_2);
    }
  }
  else if(id == (byte)81) {
    // KEY_KP3
    if(press_key) {
      Keyboard.press(KEYPAD_3);
    } else {
      Keyboard.release(KEYPAD_3);
    }
  }
  else if(id == (byte)82) {
    // KEY_KP0
    if(press_key) {
      Keyboard.press(KEYPAD_0);
    } else {
      Keyboard.release(KEYPAD_0);
    }
  }
  else if(id == (byte)83) {
    // KEY_KPDOT
    if(press_key) {
      Keyboard.press(KEYPAD_DOT);
    } else {
      Keyboard.release(KEYPAD_DOT);
    }
  }
  else if(id == (byte)86) {
    // KEY_102ND
    if(press_key) {
      Keyboard.press(KEY_NON_US);
    } else {
      Keyboard.release(KEY_NON_US);
    }
  }
  else if(id == (byte)87) {
    // KEY_F11
    if(press_key) {
      Keyboard.press(KEY_F11);
    } else {
      Keyboard.release(KEY_F11);
    }
  }
  else if(id == (byte)88) {
    // KEY_F12
    if(press_key) {
      Keyboard.press(KEY_F12);
    } else {
      Keyboard.release(KEY_F12);
    }
  }
  else if(id == (byte)96) {
    // KEY_KPENTER
    if(press_key) {
      Keyboard.press(KEYPAD_ENTER);
    } else {
      Keyboard.release(KEYPAD_ENTER);
    }
  }
  else if(id == (byte)97) {
    // KEY_RIGHTCTRL
    if(press_key) {
      Keyboard.press(KEY_RIGHT_CTRL);
    } else {
      Keyboard.release(KEY_RIGHT_CTRL);
    }
  }
  else if(id == (byte)98) {
    // KEY_KPSLASH
    if(press_key) {
      Keyboard.press(KEYPAD_DIVIDE);
    } else {
      Keyboard.release(KEYPAD_DIVIDE);
    }
  }
  else if(id == (byte)99) {
    // KEY_SYSRQ
    if(press_key) {
      Keyboard.press(KEY_PRINT);
    } else {
      Keyboard.release(KEY_PRINT);
    }
  }
  else if(id == (byte)100) {
    // KEY_RIGHTALT
    if(press_key) {
      Keyboard.press(KEY_RIGHT_ALT);
    } else {
      Keyboard.release(KEY_RIGHT_ALT);
    }
  }
  else if(id == (byte)102) {
    // KEY_HOME
    if(press_key) {
      Keyboard.press(KEY_HOME);
    } else {
      Keyboard.release(KEY_HOME);
    }
  }
  else if(id == (byte)103) {
    // KEY_UP
    if(press_key) {
      Keyboard.press(KEY_UP_ARROW);
    } else {
      Keyboard.release(KEY_UP_ARROW);
    }
  }
  else if(id == (byte)104) {
    // KEY_PAGEUP
    if(press_key) {
      Keyboard.press(KEY_PAGE_UP);
    } else {
      Keyboard.release(KEY_PAGE_UP);
    }
  }
  else if(id == (byte)105) {
    // KEY_LEFT
    if(press_key) {
      Keyboard.press(KEY_LEFT_ARROW);
    } else {
      Keyboard.release(KEY_LEFT_ARROW);
    }
  }
  else if(id == (byte)106) {
    // KEY_RIGHT
    if(press_key) {
      Keyboard.press(KEY_RIGHT_ARROW);
    } else {
      Keyboard.release(KEY_RIGHT_ARROW);
    }
  }
  else if(id == (byte)107) {
    // KEY_END
    if(press_key) {
      Keyboard.press(KEY_END);
    } else {
      Keyboard.release(KEY_END);
    }
  }
  else if(id == (byte)108) {
    // KEY_DOWN
    if(press_key) {
      Keyboard.press(KEY_DOWN_ARROW);
    } else {
      Keyboard.release(KEY_DOWN_ARROW);
    }
  }
  else if(id == (byte)109) {
    // KEY_PAGEDOWN
    if(press_key) {
      Keyboard.press(KEY_PAGE_DOWN);
    } else {
      Keyboard.release(KEY_PAGE_DOWN);
    }
  }
  else if(id == (byte)110) {
    // KEY_INSERT
    if(press_key) {
      Keyboard.press(KEY_INSERT);
    } else {
      Keyboard.release(KEY_INSERT);
    }
  }
  else if(id == (byte)111) {
    // KEY_DELETE
    if(press_key) {
      Keyboard.press(KEY_DELETE);
    } else {
      Keyboard.release(KEY_DELETE);
    }
  }
  else if(id == (byte)119) {
    // KEY_PAUSE
    if(press_key) {
      Keyboard.press(KEY_PAUSE);
    } else {
      Keyboard.release(KEY_PAUSE);
    }
  }
  else if(id == (byte)125) {
    // KEY_LEFTMETA
    if(press_key) {
      Keyboard.press(KEY_LEFT_GUI);
    } else {
      Keyboard.release(KEY_LEFT_GUI);
    }
  }
  else if(id == (byte)126) {
    // KEY_RIGHTMETA
    if(press_key) {
      Keyboard.press(KEY_RIGHT_GUI);
    } else {
      Keyboard.release(KEY_RIGHT_GUI);
    }
  }
  else if(id == (byte)127) {
    // KEY_COMPOSE
    if(press_key) {
      Keyboard.press(KEY_MENU);
    } else {
      Keyboard.release(KEY_MENU);
    }
  }
  else if(id == (byte)250) {
    // Special Key: releaseAll key
    Keyboard.releaseAll();
  }
}
