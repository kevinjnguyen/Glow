import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

bottom_servo = GPIO.PWM(12, 50)
top_servo = GPIO.PWM(33, 50)

# Calibrate servos to 0 degrees pan, 0 degrees tilt 
# 2 is zero degrees, 12.5 is 180 degrees
bottom_servo.start(2)
time.sleep(0.5)
top_servo.start(2)
time.sleep(0.5)

# HOW TO USE THIS:
# Call move_servos(top_angle, bottom_angle) to move both servos to desired position
# top_angle and bottom_angle are both float values that should range from 2 to 12.5
# 2 is 0 degrees
# 12.5 is 180 degrees
# top_angle is the desired angle of the top servo
# bottom_angle is the desired angle of the bottom servo

# HARDWARE SETUP:
# Top servo data comes from pin 33 (gpio13)
# Bottom servo data comes from pin 12 (gpio18)
# Vcc should be 6 Volts to make everything work right (trust me)

def move_servos(top_angle, bottom_angle):
  bottom_servo.ChangeDutyCycle(bottom_angle)
  # time.sleep(0.5)
  top_servo.ChangeDutyCycle(top_angle)
  #time.sleep(0.5)

# toggle_relay_status = True
# GPIO.output(31, toggle_relay_status)
try:
  while True:
#     toggle_relay_status = True
#     GPIO.output(31, toggle_relay_status)
#     # temp = input("Toggle: " )
#     # toggle_relay_status = True
#     # GPIO.output(31, toggle_relay_status)
#     # temp = input("Toggle: " )
    
    top_angle = input("Desired top angle?: ")
    bottom_angle = input("Desired bottom angle?: ")
    move_servos(float(top_angle), float(bottom_angle))
except KeyboardInterrupt:
  top_servo.stop()
  bottom_servo.stop()
  GPIO.cleanup()


