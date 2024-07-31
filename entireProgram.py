import math
import time
import signal
import threading
import argparse
import numpy as np
import board
import neopixel
from gpiozero import Button, LED
from PIL import Image, ImageEnhance
import PIL
from picamera2 import Picamera2
from libcamera import controls

from escpos.printer import Serial

pixels = neopixel.NeoPixel(board.D18, 13)
RED = 0xF00000
GREEN = 0x00F000
BLUE = 0x0000F0
PURPLE = 0xF000F0
WHITE = 0xA3A3A3
BRIGHT = 0xFFFFFF
DIM = 0x353535
OFF = 0x000000

exit_ = False
def sigint_handler(signum, frame):
    global exit_
    exit_ = True

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigint_handler)



recentBmp = False
bmpHeight = 128
bmpWidth = 128
btnShutter = Button(23)
btnPrint = Button(24)
relayPrinter = LED(26)

# 0 = R
# 1 = G
# 2 = B
# 3 = X
def setLED(color):
    global pixels
    pixels[0] = color
    pixels.show()
    return True

def flashLED(c, flashes = 5):
    global OFF
    for i in range(flashes):
        setLED(OFF)
        time.sleep(0.2)
        setLED(c)
        time.sleep(0.2)

def setRing(color):
    global pixels
    for i in range(12):
        pixels[i+1] = color
    pixels.show()

def flashRing(c, flashes = 5):
    global OFF
    for i in range(flashes):
        setRING(OFF)
        time.sleep(0.2)
        setRing(c)
        time.sleep(0.2)

def printerOn():
    global relayPrinter
    relayPrinter.off()
    
def printerOff():
    global relayPrinter
    relayPrinter.on()


def takePic():
    global RED, BRIGHT, DIM, OFF
    print('take pic')
    setLED(RED)
    setRing(BRIGHT)
    picam = Picamera2()
    picam.start(show_preview=False)
    picam.set_controls({'AfMode': controls.AfModeEnum.Continuous,'AfSpeed': controls.AfSpeedEnum.Fast})
    picam.start_and_capture_files('/home/pi/image.jpg', num_files=2, delay=0.5)
    picam.stop()
    picam.close()
    setRing(DIM)
    setRing(OFF)
    return True


def resizeImage(path, width=0, height=0):
    print('resize')
    importedImage = Image.open(path)
    w, h = importedImage.size
    gcd = math.gcd(w, h)
    wratio = w/gcd
    hratio = h/gcd
    wMax = width/wratio
    hMax = height/hratio
    mult = min(wMax, hMax)
    newWidth = math.ceil(wratio*mult)
    newHeight = math.ceil(hratio*mult)
    im = importedImage.resize((newWidth, newHeight))
    im = im.rotate(-90, PIL.Image.NEAREST, expand=1)
    return im


def convertJpgToBmp(path):
    global PURPLE, RED
    global recentBmp
    setLED(RED)
    print('convert to bmp')
    resizedImage = resizeImage(path, 640, 360)
    enhancer = ImageEnhance.Brightness(resizedImage)
    im = enhancer.enhance(1.5)
    im = im.convert('1')
    im.save("/home/pi/bitmap.bmp")
    recentBmp = True
    
    return True


def readyToRip(p):
    print('ready to rip')
    for i in range(4):
        p.textln('')

def printBmp(path):
    global BLUE
    print('print bmp')
    setLED(BLUE)
    p = Serial(devfile='/dev/ttyS0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1.00, dsrdtr=True)
    p.image(path)
    p.textln('')
    p.text(time.ctime())
    readyToRip(p)
    p.close()
    return True
    
def allPrint():
    global RED, GREEN, BLUE
    setLED(BLUE)
    printerOn()
    time.sleep(3)
    printed = printBmp("/home/pi/bitmap.bmp")
    if(printed):
        # Flash blue instead of sleeping
        flashLED(BLUE, 10)
        setLED(GREEN)
        printerOff()
    else:
        flashLED(RED)

def main():
    global RED, GREEN, BLUE
    global recentBmp, btnShutter, btnPrint, relayPrinter

    if(btnShutter.is_pressed):
        saved = takePic()
        if(saved):
            flashLED(GREEN, 2)
            converted = convertJpgToBmp("/home/pi/image.jpg")
            if(converted):
                flashLED(GREEN, 3)
                flashLED(PURPLE, 1)
                allPrint()
            else:
                flashLED(RED)
        else:
            flashLED(RED)

    if(btnPrint.is_pressed):
        allPrint()
                
setLED(GREEN)
printerOff()
while(exit_ == False):
    main()
    time.sleep(0.1)

