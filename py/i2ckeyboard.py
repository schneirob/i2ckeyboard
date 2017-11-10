import smbus
import time
import sys
import argparse
import evdev
import asyncio

bus = smbus.SMBus(1)

address = 0x10

KEY_TEST = 0b00000000
KEY_PRESS = 0b00010000
KEY_RELEASE = 0b00100000
KEY_RELEASEALL = 0b00110000

LED_ON = 0b01000000
LED_OFF = 0b00000000

def writeNumber(data):
    """Write one byte to slave on i2c bus

    Keyword arguments:
        data -- byte to send
    """
    ok = False
    try:
        bus.write_byte(address, data)
        ok = True
    except IOError:
        print("IOError on ", data, " ", end='')
        time.sleep(0.1)
    return ok

def readNumber():
    """Read one byte from slave on i2c bus

    returns data byte
    """
    ok = False
    while not ok:
        try:
            val = bus.read_byte(address)
            ok = True
        except OSError:
            print("OSError reading!", end='')
            time.sleep(0.1)
    return val

def tobit(data):
    """Convert byte to list of bit

    Keyword arguments:
        data -- byte to convert into bit list
    returns list of bit representing the data given
    """
    return [1 if d=='1' else 0 for d in bin(data)[2:]]

def bitSum(data):
    """Sum of bits in data
    returns sum
    """
    return sum(tobit(data))

def keyaction(keyid, action, led):
    """transmit key event and controll confirmation

    Keyword arguments:
        keyid -- code of key to press
        action -- action to perform (s. variables above)
        led -- led on or of (s. variable above)
    returns confirmation byte from Arduino
    """
    action = action + led

    # if checksum is even, set uneven bit
    if (bitSum(keyid) + bitSum(action)) % 2 == 0:
        action = action + 0b10000000
    # add checksum (number of bits equal 1)
    action = action + (bitSum(keyid) + bitSum(action))

    ok = True
    while True:
        ok_key = writeNumber(keyid)
        if not ok_key:
            ok = False
            continue
        ok_action = writeNumber(action)
        if ok_action:
            break
        ok = False

    confirm = readNumber()
    message = ""
    if bitSum(keyid) + bitSum(action) != confirm & 0b00001111:
        ok = False
        message = message + " Confirmed checksum failes!"
    if bitSum(confirm) % 2 == 0:
        ok = False
        message = message + " Uneven bit is set wrong in confirm!"
    if bitSum(confirm & 0b01000000) > 0:
        ok = False
        message = message + " Error bit is set!"
    if bitSum(confirm & 0b00100000) == 1:
        message = message + " Switch is on!"
    else:
        message = message + " Switch is off!"
    if bitSum(confirm & 0b00010000) == 1:
        message = message + " LED is on!"
    else:
        message = message + " LED is off!"

    if not ok:
        print(bin(keyid), " ", bin(action), " --> ", bin(confirm), " : ", message)

    return confirm

def speedtest():
    """Perform speedtest to test key press transmission on i2c bus"""

    if bitSum(keyaction(0, KEY_TEST, LED_ON) & 0b00100000) == 1:
        print("Keyboard is set to sending keys! Disable hardware switch for testing!")
        exit(1)

    now = lambda: int(round(time.time() * 1000))
    start = now()
    for i in range(0,256):
        keyaction(i, KEY_TEST, LED_ON)
        keyaction(i, KEY_PRESS, LED_ON)
        keyaction(i, KEY_RELEASE, LED_ON)
        keyaction(i, KEY_RELEASEALL, LED_ON)
    for i in range(0,256):
        keyaction(i, KEY_TEST, LED_OFF)
        keyaction(i, KEY_PRESS, LED_OFF)
        keyaction(i, KEY_RELEASE, LED_OFF)
        keyaction(i, KEY_RELEASEALL, LED_OFF)
    stop = now()
    print("%.2f"% (8.0*256.0/(stop - start)), "ms")


async def print_events(device):
    """Key event handler"""
    async for event in device.async_read_loop():
        if event.type == 1 and event.value < 2:
            # print(device.fn, evdev.categorize(event), event, sep=': ')
            move = event.value
            if event.value == 1:
                move = "key down"
                keyaction(event.code, KEY_PRESS, LED_ON)
            if event.value == 0:
                move = "key up  "
                keyaction(event.code, KEY_RELEASE, LED_ON)
            print(move, event.code, evdev.ecodes.KEY[event.code], sep='  ')


parser = argparse.ArgumentParser()
parser.add_argument("--speedtest", help="run key command transmission speed test", action="store_true")
parser.add_argument("--keyboard", help="read keyboard keys and transmit for sending to arduino", action="store_true")
args = parser.parse_args()

if args.speedtest:
    speedtest()

if args.keyboard:

    if bitSum(keyaction(0, KEY_TEST, LED_ON) & 0b00100000) == 0:
        print("Keyboard is not set to sending keys! Enable hardware switch for testing!")
        exit(1)

    devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]

    dev = False

    for device in devices:
        print(device.fn, device.name, device.phys) 
        if device.name == "HID 046a:0001":
            dev = device

    print("Selected device ", dev.fn, " for key event capture!")

    asyncio.ensure_future(print_events(dev))
    loop = asyncio.get_event_loop()
    loop.run_forever()
