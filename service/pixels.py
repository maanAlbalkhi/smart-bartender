import time
import board
import neopixel
import state as ST
 
 
# Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18
# NeoPixels must be connected to D10, D12, D18 or D21 to work.
pixel_pin = board.D18
 
# The number of NeoPixels
num_pixels = 24
 
# The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed!
# For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.
ORDER = neopixel.GRB
 
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.2, auto_write=True,
                           pixel_order=ORDER)
 
 
def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)
 
 
def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def making_wheel():
    
    pixel_delay = 0.02
    
    pixel_1 = (0, 0, 10)
    pixel_2 = (0, 0, 30)
    pixel_3 = (0, 0, 200)
    pixel_4 = (0, 0, 30)
    pixel_5 = (0, 0, 10)
    
    start = time.time()
    
    while ((time.time()- start) < ST.duration):
        if ST.cancel == True:
            return
        
        '''
        next_time = time.time()
        while not ST.is_glass:
            if ST.cancel == True:
               break
            delay = time.time()-next_time
        start += delay
        '''
        for i in range(24):
            delay = 0
            next_time = time.time()
            while not ST.is_glass:
                if ST.cancel == True:
                    return
                
                pixels.fill((150,0,0))
                pixels.show()
                
                delay = time.time()-next_time
            start += delay
            
            pixels.fill((10,20,0))
            pixels[i % 24] = pixel_1
            pixels[(i+1) % 24] = pixel_2
            pixels[(i+2) % 24] = pixel_3
            pixels[(i+3) % 24] = pixel_4
            pixels[(i+4) % 24] = pixel_5
            pixels.show()
            time.sleep(pixel_delay)
            
def blink_green():
    delay = 0.0001
    count = 0
    while count < 2:
        for i in range(255, 20, -1):
                pixels.fill((0,i,0))
                pixels.show()
                time.sleep(delay)
        for i in range(20, 255, 1):
                pixels.fill((0,i,0))
                pixels.show()
                time.sleep(delay)
        count += 1
        
def blink_red():
    red_delay = 0.002
    for i in range(255, 20, -1):
        pixels.fill((i,0,0))
        pixels.show()
        time.sleep(red_delay)
    for i in range(20, 255, 1):
        pixels.fill((i,0,0))
        pixels.show()
        time.sleep(red_delay)
            
def half_green():
    pixels.fill((0,0,0))
    pixels.show()
    for i in range(24):
        if (i%2) == 0:
            pixels[i] = (0,255,0)
    pixels.show()
    
if __name__ == "__main__":
    while True:
        blink_red()
