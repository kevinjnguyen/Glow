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

class current_line:
    def __init__(self, current_line):
        self.current_line = current_line
        self.did_start_new_line = False

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

bottom_servo = GPIO.PWM(12, 50)
top_servo = GPIO.PWM(33, 50)

mutex = Lock()

queue = deque()
line = current_line(0)

def laser_on():
    GPIO.output(31, True)

def laser_off():
    GPIO.output(31, False)

def recenter():
    move_servos(0, 0)

def angle_to_pwm_pan(angle):
    return 7.194 + (angle * -3.066)

def angle_to_pwm_tilt(angle):
    return 6.762 + (angle * -3.303)

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
        try:
            queue.append(request)
        finally:
            mutex.release()
        return grpc_pb2.GlowReply(message='Receieved!')

    def LotsOfPoints(self, request_iterator, context):
        for new_point in request_iterator:
            print('(' + str(new_point.x1) + ', ' + str(new_point.y1) + ') ----> ' + '(' + str(new_point.x2) + ', ' + str(new_point.y2))
        return grpc_pb2.GlowReply(message='Receieved!')


def processData():
    mutex.acquire()
    global current_line
    try:
        if len(queue) > 0:
            request = queue.popleft()

            if request.line != line.current_line:
                laser_off()
                line.current_line = request.line
                line.did_start_new_line = True
            else:
                laser_on()
            
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
        if (line.did_start_new_line):
            time.sleep(0.35)
            line.did_start_new_line = False
        

if __name__ == '__main__':
    logging.basicConfig()
    serve()

