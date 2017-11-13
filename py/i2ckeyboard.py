# vim: set fileencoding=utf-8

import time
import sys
from termios import tcflush, TCIOFLUSH
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
                move = "key down"
                keyboard.keyAction(event.code,
                                   keyboard.KEY_PRESS,
                                   keyboard.LED_ON)
            if event.value == 0:
                move = "key up  "
                keyboard.keyAction(event.code,
                                   keyboard.KEY_RELEASE,
                                   keyboard.LED_ON)
            log.debug(move +
                      str(event.code) +
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
    return parser


if __name__ == '__main__':

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
        keyboard.sendText(
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ" + "\n" +
                "abcdefghijklmnopqrstuvwxyz" + "\n" +
                "0123456789" + "\n"
                )

        for k, v in KEY_MAP.items():
            for key in v:
                keyboard.press(key)
                time.sleep(0.01)
            keyboard.releaseAll()
