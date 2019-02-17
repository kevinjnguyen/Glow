from concurrent import futures
from threading import Thread, Lock
from datetime import datetime

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

# -------------clockwork------------------- dorick branch BEGIN

# ---definitions


def get_unit():
    return .9875
    # 1 unit is .9875


def down_length():
    return -5*get_unit()
    # add coordinate to move down


def up_length():
    return 5*get_unit()
    # give coordinate to move up


def rigth_width():
    return 3*get_unit()
    # give coordinate to move up


def left_width():
    return -3*get_unit()
    # give coordinate to move up


# --- Returning our starting positions that we would start at
def goToFirstPosit():
    req = {}
    req['x2'] = -7*get_unit()
    req['y2'] = 5*get_unit()
    return req


def goToSecondPosit():
    req = {}
    req['x2'] = -3*get_unit()
    req['y2'] = 5*get_unit()
    return req


def goToThirdPosit():
    req = {}
    req['x2'] = get_unit()
    req['y2'] = 5*get_unit()
    return req


def goToLastPosit():
    req = {}
    req['x2'] = 5*get_unit()
    req['y2'] = 5*get_unit()
    return req


def goToCenter():
    req = {}
    req['x2'] = float(0)
    req['y2'] = float(0)
    return req

# --- Number movement methods


def move_to_coordinates(request):
    pan_angle, tilt_angle = scale_box_to_pan_tilt(request)
    pan_pwm = angle_to_pwm_pan(pan_angle)
    tilt_pwm = angle_to_pwm_tilt(tilt_angle)
    move_servos(pan_pwm, tilt_pwm)
    time.sleep(0.5)


def draw_num_0(position):
    laser_off()
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


def num_1(position):
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

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    laser_on()

    req['y2'] += down_length()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    # req['x2'] += rigth_width()
    # move_to_coordinates(req)
    # req['y2'] += up_length()
    # move_to_coordinates(req)
    # req['y2'] += up_length()
    # move_to_coordinates(req)
    # req['x2'] += left_width()
    # move_to_coordinates(req)

    laser_off()

    return "1"


def num_2(position):
        req = {}
        if(position == 0):
            req = goToFirstPosit()
        elif(position == 1):
            req = goToSecondPosit()
        elif(position == 2):
            req = goToThirdPosit()
        else:
            req = goToLastPosit()

        # corner
        move_to_coordinates(req)

        #
        laser_on()

        req['x2'] += rigth_width()
        move_to_coordinates(req)
        req['y2'] += down_length()
        move_to_coordinates(req)
        req['x2'] += left_width()
        move_to_coordinates(req)
        req['y2'] += down_length()
        move_to_coordinates(req)
        req['x2'] += rigth_width()
        move_to_coordinates(req)

        laser_off()

        return "2"


def num_3(position):
        req = {}
        if(position == 0):
            req = goToFirstPosit()
        elif(position == 1):
            req = goToSecondPosit()
        elif(position == 2):
            req = goToThirdPosit()
        else:
            req = goToLastPosit()

        # corner
        move_to_coordinates(req)

        #
        laser_on()

        req['x2'] += rigth_width()
        move_to_coordinates(req)
        req['y2'] += down_length()
        move_to_coordinates(req)
        req['x2'] += left_width()
        move_to_coordinates(req)

        laser_off()

        req['x2'] += rigth_width()
        move_to_coordinates(req)

        laser_on()

        req['y2'] += down_length()
        move_to_coordinates(req)
        req['x2'] += left_width()
        move_to_coordinates(req)

        laser_off()
        return "3"


def num_4(position):
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
    req['x2'] += rigth_width()
    move_to_coordinates(req)
    req['y2'] += up_length()
    move_to_coordinates(req)

    laser_off()

    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_on()

    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_off()

    return "4"


def num_5(position):
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

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    laser_on()

    req['x2'] += left_width()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    req['y2'] += down_length()
    move_to_coordinates(req)
    req['x2'] += left_width()
    move_to_coordinates(req)

    laser_off()

    return "5"


def num_6(position):
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

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    laser_on()

    req['x2'] += left_width()
    move_to_coordinates(req)

    req['y2'] += down_length()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    req['y2'] += up_length()
    move_to_coordinates(req)

    req['x2'] += left_width()
    move_to_coordinates(req)

    laser_off()

    return "6"


def num_7(position):
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

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    req['y2'] += down_length()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_off()

    return "7"


def num_8(position):
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

    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_on()

    req['x2'] += rigth_width()
    move_to_coordinates(req)

    laser_off()

    return "8"


def num_9(position):
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

    req['x2'] += rigth_width()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_on()

    req['x2'] += left_width()
    move_to_coordinates(req)
    req['y2'] += up_length()
    move_to_coordinates(req)
    req['x2'] += rigth_width()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)
    req['y2'] += down_length()
    move_to_coordinates(req)

    laser_off()

    return "9"


def draw_time():
    now = datetime.now()
    hour = (now.hour) % 12
    minute_str = now.strftime("%M")
    # draw the hours
    if(hour == 1):
        draw_num_0(0)
        num_1(1)
    elif(hour == 2):
        draw_num_0(0)
        num_2(1)
    elif(hour == 3):
        draw_num_0(0)
        num_3(1)
    elif(hour == 4):
        draw_num_0(0)
        num_4(1)
    elif(hour == 5):
        draw_num_0(0)
        num_5(1)
    elif(hour == 6):
        draw_num_0(0)
        num_6(1)
    elif(hour == 7):
        draw_num_0(0)
        num_7(1)
    elif(hour == 8):
        draw_num_0(0)
        num_8(1)
    elif(hour == 9):
        draw_num_0(0)
        num_9(1)
    elif(hour == 10):
        num_1(0)
        draw_num_0(1)
    elif(hour == 11):
        num_1(0)
        num_1(1)
    elif(hour == 12):
        num_1(0)
        num_2(1)

    # draw first minute
    if(int(minute_str[0]) == 0):
        draw_num_0(2)
    elif(int(minute_str[0]) == 1):
        num_1(2)
    elif(int(minute_str[0]) == 2):
        num_2(2)
    elif(int(minute_str[0]) == 3):
        num_3(2)
    elif(int(minute_str[0]) == 4):
        num_4(2)
    elif(int(minute_str[0]) == 5):
        num_5(2)

    # draw second minute
    if(int(minute_str[1]) == 0):
        draw_num_0(3)
    elif(int(minute_str[1]) == 1):
        num_1(3)
    elif(int(minute_str[1]) == 2):
        num_2(3)
    elif(int(minute_str[1]) == 3):
        num_3(3)
    elif(int(minute_str[1]) == 4):
        num_4(3)
    elif(int(minute_str[1]) == 5):
        num_5(3)
    elif(int(minute_str[1]) == 6):
        num_6(3)
    elif(int(minute_str[1]) == 7):
        num_7(3)
    elif(int(minute_str[1]) == 8):
        num_8(3)
    elif(int(minute_str[1]) == 9):
        num_9(3)


# -------------clockwork------------------- dorick branch END

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

    def DrawTime(self, request, context):
        draw_time()
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
