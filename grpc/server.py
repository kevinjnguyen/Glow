from concurrent import futures
from threading import Thread, Lock

import RPi.GPIO as GPIO
import time
import logging
import math
import grpc

import grpc_pb2
import grpc_pb2_grpc

from collections import deque

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

bottom_servo = GPIO.PWM(12, 50)
top_servo = GPIO.PWM(33, 50)

mutex = Lock()

queue = deque()

# -------------clockwork------------------- dorick branch BEGIN

#---definitions
def unit():
    return .9875
    # 1 unit is .9875

def down_length():
    return -5*unit()
    #add coordinate to move down

def up_length():
    return 5*unit()
    #give coordinate to move up

def rigth_width():
    return 3*unit()
    #give coordinate to move up

def left_width():
    return -3*unit()
    #give coordinate to move up


#--- Returning our starting positions that we would start at
def goToFirstPosit():
	req = {}
	req['x2'] = (-7*unit())
	req['y2'] = (5*unit())
    #return ((-7*.9875),(5*.9875))
    return req

def goToSecondPosit():
	req = {}
	req['x2'] = (-3*unit())
	req['y2'] = (5*unit())
    #return ((-3*.9875),(5*.9875))
    return req

def goToThirdPosit():
	req = {}
	req['x2'] = unit()
	req['y2'] = (5*unit())
    #return ((.9875),(5*.9875))
    return req

def goToLastPosit():
	req = {}
	req['x2'] = (5*unit())
	req['y2'] = (5*unit())
    #return ((5*.9875),(5*.9875))
    return req

def center():
	req = {}
	req['x2'] = float(0)
	req['y2'] = float(0)
	return req

#--- Number movement methods

def move_to_coordinates(req):
	pan_angle, tilt_angle = scale_box_to_pan_tilt(req)
    pan_pwm = angle_to_pwm_pan(pan_angle)
    tilt_pwm = angle_to_pwm_tilt(tilt_angle)
    move_servos(pan_pwm, tilt_pwm)

def num_0(position):
    req = {}
    if(position == 0):
    	req = goToFirstPosit()
    elif(position == 1):
    	req = goToSecondPosit()
    elif(position == 2):
    	req = goToThirdPosit()
    else:
    	req = goToLastPosit()

    move_to_coordinates(req)

    laser_on()

    req['y2'] += down_length()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)
    req['x2'] += rigth_width()
    move_to_coordinates(req)
    req['y2'] += up_length()
    move_to_coordinates(req)
    req['y2'] += up_length()
    move_to_coordinates(req)
    req['x2'] += left_width()
    move_to_coordinates(req)

    laser_off()

    return "0"

def num_1():
    # grab corner start location
    grab()
    #yolo random thing method
    move_method(rigth_width,(5*.9875))
    laser_on()
    move_method(0,down_length())
    move_method(0,down_length())
    laser_off()
    return "1"

def num_2():
    grab()
    #yolo random thing method
    move_method(rigth_width,(5*.9875))

def clockwork():


# -------------clockwork------------------- dorick branch END

def laser_on():
    GPIO.output(31, True)

def laser_off():
    GPIO.output(31, False)

def recenter():
    move_servos(0, 0)

def angle_to_pwm_pan(angle):
    return 7.75 + (angle * -2.47)

def angle_to_pwm_tilt(angle):
    return 7.75 + (angle * -2.47)

def move_servos(pan_pwm, tilt_pwm):
    bottom_servo.ChangeDutyCycle(pan_pwm)
    top_servo.ChangeDutyCycle(tilt_pwm)
    return ""

def scale_ipad_to_box(request):
    result = {}
    result['x1'] = (request.x1/10.0 - 384.0) / 39.38
    result['x2'] = (request.x2/10.0 - 384.0) / 39.38
    result['y1'] = (request.y1/10.0 - 640.0) / -39.38
    result['y2'] = (request.y2/10.0 - 640.0) / -39.38
    return result

def scale_box_to_pan_tilt(request):
    pan_angle = math.atan(request['x2'] / 9.75)
    tilt_angle = (math.pi / 2) - math.acos(request['y2'] / math.sqrt( request['x2'] ** 2 + request['y2'] **2 + 9.75**2))
    return pan_angle, tilt_angle


class Greeter(grpc_pb2_grpc.GlowServicer):

    def TestPointReceiving(self, request, context):
        mutex.acquire()
        print('Server: Acquired the lock.')
        try:
            queue.append(request)
        finally:
            print('Server: Released the lock.')
            mutex.release()
        return grpc_pb2.GlowReply(message='Receieved!')

    def LotsOfPoints(self, request_iterator, context):
        for new_point in request_iterator:
            print('(' + str(new_point.x1) + ', ' + str(new_point.y1) + ') ----> ' + '(' + str(new_point.x2) + ', ' + str(new_point.y2))
        return grpc_pb2.GlowReply(message='Receieved!')


def processData():
    mutex.acquire()
    try:
        if len(queue) > 0:
            print('Should be moving...')
            request = queue.popleft()
            box_scaled = scale_ipad_to_box(request)
            pan_angle, tilt_angle = scale_box_to_pan_tilt(box_scaled)
            pan_pwm = angle_to_pwm_pan(pan_angle)
            tilt_pwm = angle_to_pwm_tilt(tilt_angle)
            move_servos(pan_pwm, tilt_pwm)
    finally:
        mutex.release()
    return 'Done'

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb2_grpc.add_GlowServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    laser_on()
    recenter()

    bottom_servo.start(2)
    time.sleep(0.5)
    top_servo.start(2)
    time.sleep(0.5)

    try:
        while True:
            polling()
            time.sleep(_ONE_DAY_IN_SECONDS)
        
    except KeyboardInterrupt:
        laser_off()
        top_servo.stop()
        bottom_servo.stop()
        GPIO.cleanup()
        server.stop(0)

def polling():
    while True:
        p = Thread(target = processData)
        p.start()
        

if __name__ == '__main__':
    logging.basicConfig()
    serve()

