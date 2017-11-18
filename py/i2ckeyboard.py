# vim: set fileencoding=utf-8

import time
import sys
from termios import tcflush, TCIOFLUSH
import termios
import tty
import argparse
import evdev
import asyncio
import logging

import i2ctransmit
from keymap import KEY_MAP
from keyevents import *

address = 0x10  # I2C/TWI hardwareadress of keyboard


async def handleEvents(device):
    '''Key event handler'''
    async for event in device.async_read_loop():
        if event.type == 1 and event.value < 2:
            move = event.value
            if event.value == 1:
                move = "key down  "
                keyboard.keyAction(event.code,
                                   keyboard.KEY_PRESS,
                                   keyboard.LED_ON)
            if event.value == 0:
                move = "key up    "
                keyboard.keyAction(event.code,
                                   keyboard.KEY_RELEASE,
                                   keyboard.LED_ON)
            log.debug(move +
                      str(event.code) + " - " +
                      str(evdev.ecodes.KEY[event.code]))
            if keyboard.pressedKeys() == [KEY_E, KEY_X, KEY_I, KEY_T,
                                          KEY_RIGHTSHIFT, KEY_1]:
                log.info("'exit!' detected, exiting")
                loop.stop()
                keyboard.releaseAll()

            tcflush(sys.stdin, TCIOFLUSH)


def createParser():
    '''Create parser and fill with needed commands'''
    parser = argparse.ArgumentParser()
    parser.add_argument("--log",
                        help="select log level",
                        choices=["DEBUG", "INFO", "ERROR", "WARNING",
                                 "debug", "info", "error", "warning"],
                        type=str,
                        default="INFO",
                        action="store")
    parser.add_argument("--speedtest",
                        help="run key command transmission speed test",
                        action="store_true")
    parser.add_argument("--keyboard",
                        help="read keyboard keys and transmit for " +
                             "sending to arduino",
                        action="store_true")
    parser.add_argument("--sendtext",
                        help="Send sample characters for testing",
                        action="store_true")
    parser.add_argument("--keyreflect",
                        help="Plug Arduino keyboard into pi and test if keys" +
                             " are send correctly!",
                        action="store_true")
    return parser


def getchr(test):
    '''Write test to keyboard and read one character from stdin'''
    fd = sys.stdin.fileno()
    old_set = termios.tcgetattr(fd)
    ch = None
    try:
        tty.setraw(fd)
        keyboard.sendText(test)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_set)

    tcflush(sys.stdin, TCIOFLUSH)
    log.debug("Received input: '" + ch + "'!")
    return ch


if __name__ == '__main__':

    testchars = ['\n',
                 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
                 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                 'w', 'x', 'y', 'z', '\n',
                 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K',
                 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                 'W', 'X', 'Y', 'Z', '\n',
                 'ü', 'ö', 'ä', 'Ü', 'Ö', 'Ä', '\n',
                 '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '\n',
                 '!', '"', '§', '$', '%', '&', '/', '(', ')', '=', '\n',
                 '¹', '²', '³', '¼', '½', '{', '[', ']', '}', '\n',
                 '€', 'µ', '@', '«', '»', '„', '“', '”', '·', '…', '\n',
                 ',', ';', '.', ':', '-', '_', '<', '>', '|', 'ß', '?', '\n',
                 '\\', '`', '+', '*', '~', '#', '\'', '^', '°', ' ', '\n',
                 'ê', 'é', 'è', 'ô', 'ó', 'ò', 'â', 'á', 'à', 'î', 'í',
                 'ì', 'û', 'ú', 'ù', '\n',
                 'Ê', 'É', 'È', 'Ô', 'Ó', 'Ò', 'Î', 'Í', 'Ì', 'Û', 'Ú',
                 'Ù', 'Â', 'Á', 'À', '\n',
                 'ẑ', 'Ẑ', 'ź', 'Ź', 'ĉ', 'Ĉ', 'ć', 'Ć', 'ŝ', 'Ŝ', 'ĵ',
                 'Ĵ', 'ĥ', 'Ĥ', 'ĝ', 'Ĝ', 'ŷ', 'Ŷ', '\n']

    parser = createParser()
    args = parser.parse_args()

    loglevel = getattr(logging, args.log.upper(), None)
    if not isinstance(loglevel, int):
        raise ValueError('Invalid log level "%s"' % args.log)
    logging.basicConfig(
            level=loglevel)
    log = logging.getLogger(__name__)

    keyboard = i2ctransmit.I2cTransmit(address)

    if args.speedtest:
        keyboard.i2cSpeedtest()

    if args.keyboard:

        if not keyboard.keyboardEnabled():
            log.warning("Keyboard is not set to sending keys!" +
                        "Enable hardware switch for testing!")

        devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
        dev = False
        for device in devices:
            log.info(str(device.fn) + " " +
                     str(device.name) + " " +
                     str(device.phys))
            if device.name == "HID 046a:0001":
                dev = device

        log.info("Selected device " + str(dev.fn) + " for key event capture!")
        log.warning("Ctrl-C disabled!")
        log.warning("Press and HOLD 'e' 'x' 'i' 't' 'RightShift' 1' to exit!")

        asyncio.ensure_future(handleEvents(dev))
        loop = asyncio.get_event_loop()
        sigint_detect = True
        while sigint_detect:
            sigint_detect = False
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                sigint_detect = True
            tcflush(sys.stdin, TCIOFLUSH)

    if args.sendtext:

        if not keyboard.keyboardEnabled():
            log.warning("Keyboard is not set to sending keys!" +
                        "Enable hardware switch for testing!")

        for c in testchars:
            keyboard.sendText(c)

    if args.keyreflect:

        if not keyboard.keyboardEnabled():
            log.warning("Keyboard is not set to sending keys!" +
                        "Enable hardware switch for testing!")
            exit(0)

        s = 0  # success
        sstr = ""
        f = 0  # failure
        fstr = ""
        start = keyboard._now()
        for c in testchars:
            if c is '\n':
                continue
            if getchr(c) == c[0] :
                log.debug("Success testing '" + c + "'!")
                s += 1
                sstr += c[0]
            else:
                log.debug("Failed testing '" + c + "'!")
                f += 1
                fstr += c[0]

        stop = keyboard._now()

        log.info("Successfully send/received " + str(s) + " chars (" +
                 sstr + ") !")
        log.info(str(f) + " chars failed to successfully transmit (" +
                 fstr + ") !")
        log.info("Time required: " + str(stop - start) + " ms")
        if s > 0:
            log.info("Time required: " + "%.2f" % ((stop - start)/s) +
                     " ms/key")
            log.info("Key speed achieved: " +
                     "%.2f" % (1/((stop - start)/s/1000)) +
                     " keys/s")
