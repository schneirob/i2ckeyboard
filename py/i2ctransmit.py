import smbus
import time
import logging

from keymap import KEY_MAP


class I2cTransmit:
    '''
    Transmit keypress and keyrelease events to an Arduino Micro and trigger
    keyevents on the Arduino Micro HID. See README.md for description of the
    transmission "protocol".
    '''

    KEY_TEST = 0b00000000
    KEY_PRESS = 0b00010000
    KEY_RELEASE = 0b00100000
    KEY_RELEASEALL = 0b00110000

    LED_ON = 0b01000000
    LED_OFF = 0b00000000

    DEVICE_ID = 0b10000010

    def __init__(self, address):
        '''
        Initialize i2ctransmit Object

        Keyword arguments:
            address -- address of Arduino Micro on I2C/TWI bus
        '''
        self.pressed_keys = []        # List of currently pressed keys
        self.address = address        # i2c/TWI hardware address of keyboard
        self.bus = smbus.SMBus(1)     # use '0' on first gen raspberry pi's
        self.log = logging.getLogger(__name__)
        self.is_keyboard = False      # True if keyboard is verified
        self.checkKeyboard()          # try to verify keyboard @ address

    def checkKeyboard(self):
        '''
        Check if the given i2c address returns self.DEVICE_ID when
        no writing action has been beformed before.
        Check if a test keypress results in the expected answer.
        '''
        ok = False
        dev_id = None
        retry = 0
        error_OSError = 0
        error_Exception = 0
        while not ok and retry < 10:
            try:
                dev_id = self.readByte()
                ok = True
            except OSError as e:
                error_OSError += 1
            except Exception as e:
                self.log.exception("checkKeyboard: Unexpected error!")
            retry += 1

        if error_OSError > 0:
            self.log.error("checkKeyboard: " + str(error_OSError) +
                           "x : Error reading 'DEVICE_ID'" +
                           " from address " + hex(self.address) + "!")

        if not ok:
            self.is_keyboard = False
            self.log.error("checkKeyboard: failed to verify i2ckeyboard" +
                           " on address " + hex(self.address) + "!")
            return self.is_keyboard

        if dev_id != self.DEVICE_ID:
            self.is_keyboard = False
            self.log.error("checkKeyboard: failed to verify i2ckeyboard" +
                           " on address " + hex(self.address) + "!")
            return self.is_keyboard

        self.is_keyboard = True  # temporarily enable for testing!!

        retry = 0
        ret = False
        while ret is False and retry < 10:
            ret = self.keyAction(0, self.KEY_TEST, self.LED_OFF)
            retry += 1

        if ret is False:
            self.is_keyboard = False
            self.log.error("checkKeyboard: failed to verify i2ckeyboard" +
                           " on address " + hex(self.address) + "!")
            return self.is_keyboard

        (ok, confirm) = ret
        if ok:
            self.is_keyboard = True
            self.log.info("checkKeyboard: successfully verified i2ckeyboard" +
                          " on address " + hex(self.address) + "!")

        return self.is_keyboard

    def writeByte(self, data):
        '''
        Write one byte to slave on i2c bus

        Keyword arguments:
            data -- byte to send
        '''
        self.bus.write_byte(self.address, data)
        return True

    def readByte(self):
        '''
        Read one byte from slave on i2c bus

        returns data byte
        '''
        val = self.bus.read_byte(self.address)
        return val

    def tobit(self, data):
        '''
        Convert byte to list of bit

        Keyword arguments:
            data -- byte to convert into bit list
        returns list of bit representing the data given
        '''
        return [1 if d == '1' else 0 for d in bin(data)[2:]]

    def bitSum(self, data):
        '''
        Sum of bits in data
        returns sum
        '''
        return sum(self.tobit(data))

    def pressedKeys(self):
        '''
        returns a list of currently pressed keys
        '''
        return self.pressed_keys

    def press(self, keyid):
        '''
        Press key with given keyid
        '''
        return self.keyAction(keyid, self.KEY_PRESS, self.LED_ON)

    def release(self, keyid):
        '''
        Release key with given keyid
        '''
        return self.keyAction(keyid, self.KEY_RELEASE, self.LED_ON)

    def releaseAll(self):
        '''
        Release all keys

        returns True on success
        '''
        if not self.is_keyboard:
            return False

        retry = 0
        ret = False
        while ret is False and retry < 10:
            ret = self.keyAction(0, self.KEY_RELEASEALL, self.LED_ON)
            retry += 1
        if ret is False:
            return False
        return True

    def keyboardEnabled(self):
        '''
        Check the status of the hardware switch

        returns True, when key events are forwarded to HID
        '''
        if not self.is_keyboard:
            return False

        retry = 0
        ret = False
        while ret is False and retry < 10:
            ret = self.keyAction(0, self.KEY_TEST, self.LED_OFF)
            retry += 1
        if ret is False:
            return False
        return self.switch

    def checkConfirm(self, keyid, action, confirm):
        '''
        Perform confirmation checks on reveiced confirmation byte
        returns True, when all checks performed as expected
        '''
        message = ""
        ok = True

        if self.bitSum(keyid) + self.bitSum(action) != confirm & 0b00001111:
            ok = False
            message = message + " Confirmed checksum failes!"

        if self.bitSum(confirm) % 2 == 0:
            ok = False
            message = message + " Uneven bit is set wrong in confirm!"

        if self.bitSum(confirm & 0b01000000) > 0:
            ok = False
            message = message + " Error bit is set!"

        if ok:
            if self.bitSum(confirm & 0b00100000) == 1:
                message = message + " Switch is on!"
                self.switch = True
            else:
                message = message + " Switch is off!"
                self.switch = False

            if self.bitSum(confirm & 0b00010000) == 1:
                message = message + " LED is on!"
                self.led = True
            else:
                message = message + " LED is off!"
                self.led = False

            self.log.debug(bin(keyid) + " " + bin(action) + " --> " +
                           bin(confirm) + " : " + message)
        else:
            self.log.warning(bin(keyid) + " " + bin(action) + " --> " +
                             bin(confirm) + " : " + message)
        return ok

    def keyAction(self, keyid, action, led):
        '''
        transmit key event and controll confirmation

        Keyword arguments:
            keyid -- code of key to press
            action -- action to perform (s. variables above)
            led -- led on or of (s. variable above)
        returns:
            False on transmission error
            (ok, confirm) on transmission success
                ok -- checksum and uneven bit as expected
                confirm -- confirmation response byte
        '''
        if not self.is_keyboard:
            return False

        _action = action
        action = action + led

        # if checksum is even, set uneven bit
        if (self.bitSum(keyid) + self.bitSum(action)) % 2 == 0:
            action = action + 0b10000000

        # add checksum (number of bits equal 1)
        action = action + (self.bitSum(keyid) + self.bitSum(action))

        # send key id to Arduino Micro
        try:
            self.writeByte(keyid)
        except IOError as e:
            self.log.error("keyAction: Error writing 'keyid' " +
                           bin(keyid) + " to " +
                           "address " + hex(self.address) + "!")
            return False
        except Exception as e:
            self.log.exception("keyAction: Unexpected error!")
            return False

        # send action request to Arduino Micro
        try:
            self.writeByte(action)
        except IOError as e:
            self.log.error("keyAction: Error writing 'action' " +
                           bin(action) + " to " +
                           "address " + hex(self.address) + "!")
            return False
        except Exception as e:
            self.log.exception("keyAction: Unexpected error!")
            return False

        # read confirmation response from Arduino Micro
        try:
            confirm = self.readByte()
        except OSError as e:
            self.log.error("keyAction: Error reading 'confirm' from " +
                           "address " + hex(self.address) + "!")
            return False
        except Exception as e:
            self.log.exception("keyAction: Unexpected error!")
            return False

        ok = self.checkConfirm(keyid, action, confirm)

        if ok:
            if _action == self.KEY_PRESS:
                self.pressed_keys.append(keyid)
            elif _action == self.KEY_RELEASE:
                self.pressed_keys = [k for k in self.pressed_keys
                                     if k is not keyid]
            elif _action == self.KEY_RELEASEALL:
                self.pressed_keys = []
            self.log.debug("Pressed keys: " + str(self.pressed_keys))

        return (ok, confirm)

    def _now(self):
        '''Return current time in Microseconds'''
        return int(round(time.time() * 1000))

    def i2cSpeedtest(self):
        '''
        Perform speedtest to test key press transmission on i2c bus
        Disabled hardware key is enforced. This test is running all
        possible keyids in numeric order and would cause unforseeable
        effects, if these would become key events on any machine!
        '''

        if not self.is_keyboard:
            self.log.warning("i2cSpeedtest: Run checkKeyboard() first to " +
                             "verify that an Arduino Keyboard is connected!")
            return False

        if self.keyboardEnabled():
            self.log.warning("i2cSpeedtest: Keyboard is set to sending keys!" +
                             " Disable hardware switch for testing!")
            return False

        c = 0
        self.log.info("i2cSpeedtest: Starting test!")
        start = self._now()
        for ledstatus in [self.LED_ON, self.LED_OFF]:
            for keyid in range(0, 256):
                for keyaction in [self.KEY_TEST, self.KEY_PRESS,
                                  self.KEY_RELEASE, self.KEY_RELEASEALL]:
                    ok = False
                    retry = 0
                    while not ok and retry < 10:
                        ok = self.keyAction(keyid, keyaction, ledstatus)
                        retry += 1
                        if not ok:
                            time.sleep(0.1)
                    if ok:
                        c += 1
        stop = self._now()
        self.log.info("i2cSpeedtest: Test duration: %.2f ms", (stop - start))
        self.log.info("i2cSpeedtest: Performed %.0f successfull transmissions",
                      c)
        if c > 0:
            self.log.info("i2cSpeedtest: %.2f ms/keyaction",
                          (stop - start) * 1.00 / c)
            self.log.info("i2cSpeedtest: %.2f keyactions/s",
                          (1 / ((stop - start) * 1.00 / c / 1000)))
        return

    def sendText(self, text):
        '''
        Translate the given text into keyboard events and create them
        via the i2c interface.

        Keyword arguments:
            text -- text to send / write with the keyboard
        '''

        if not self.is_keyboard:
            self.log.warning("sendText: Run checkKeyboard() first to " +
                             "verify that an Arduino Keyboard is connected!")
            return False

        for char in text:
            keylist = ()
            try:
                keylist = KEY_MAP[char]
            except:
                self.log.warning("sendText: Could not find '" + char + "' " +
                                 "in KEY_MAP!")
                continue

            if not isinstance(keylist, tuple):
                continue

            for key in keylist:
                self.press(key)
                time.sleep(0.001)
            self.releaseAll()
            time.sleep(0.001)

        return
