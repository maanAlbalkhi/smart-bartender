import RPi.GPIO as GPIO
import threading
import time
import state as ST

#GPIO.setmode(GPIO.BOARD)
#main_switch_1 = 37
#main_switch_2 = 40
#motors = {"1":16, "2":18, "3":22, "4":32, "5":36, "6":38,
#          "7":35, "8":33, "9":31, "10":29, "11":15, "12":13}
main_switch_1 = 26
main_switch_2 = 21
ir_sensor = 17
motors={"1":23,
        "2":24,
        "3":25,
        "4":12,
        "5":16,
        "6":20,
        "7":19,
        "8":13,
        "9":6,
        "10":5,
        "11":22,
        "12":27}

def glass_status_check():
    while True:
        ST.is_glass = GPIO.input(ir_sensor)
        time.sleep(0.2)

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ir_sensor, GPIO.IN)
    GPIO.setup(main_switch_1, GPIO.OUT)
    GPIO.setup(main_switch_2, GPIO.OUT)
    for num in motors:
        GPIO.setup(motors[num], GPIO.OUT)
    threading.Thread(target=glass_status_check).start()

def switch_off(pin):
    GPIO.output(pin, GPIO.HIGH)

def motor_off(tray):
    switch_off(motors[tray])

def all_motors_off():
    for num in motors:
        motor_off(num)

def all_off():
    switch_off(main_switch_1)
    switch_off(main_switch_2)
    all_motors_off()
    
def switch_on(pin):
    GPIO.output(pin, GPIO.LOW)

def motor_on(tray):
    switch_on(motors[tray])

def all_motors_on():
    for num in motors:
        motor_on(num)

def all_on():
    all_motors_on()
    switch_on(main_switch_1)
    switch_on(main_switch_2)

def reverse(tray):
    all_on()
    motor_off(motors[tray])
    
def cleanup():
    GPIO.cleanup()

if __name__ == '__main__':
    init()
    GPIO.setup(3, GPIO.OUT)
    GPIO.output(3, GPIO.LOW)
    time.sleep(3)
    GPIO.output(3, GPIO.HIGH)
    cleanup()
