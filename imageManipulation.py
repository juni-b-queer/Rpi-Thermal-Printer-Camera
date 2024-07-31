import math

import numpy as np
from PIL import Image, ImageEnhance
import PIL

def resizeImage(path, width=0, height=0):
    print('resize')
    importedImage = Image.open(path)
    w, h = importedImage.size
    gcd = math.gcd(w, h)
    wratio = w / gcd
    hratio = h / gcd
    wMax = width / wratio
    hMax = height / hratio
    mult = min(wMax, hMax)
    newWidth = math.ceil(wratio * mult)
    newHeight = math.ceil(hratio * mult)
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


