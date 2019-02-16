from concurrent import futures
from threading import Thread, Lock

import RPi.GPIO as GPIO
import time
import logging
import math
import grpc

import grpc_pb2
import grpc_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
GPIO.setmode(GPIO.BOARD)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)

bottom_servo = GPIO.PWM(12, 50)
top_servo = GPIO.PWM(33, 50)

def laser_on():
    GPIO.output(31, True)

def laser_off():
    GPIO.output(31, False)

class Greeter(grpc_pb2_grpc.GlowServicer):

    mutex = Lock()

    def scale_ipad_to_box(self, request):
        request.x1 = (request.x1 - 384.0) / 39.38
        request.x2 = (request.x2 - 384.0) / 39.38
        request.y1 = (request.y1 - 640.0) / -39.38
        request.y2 = (request.y2 - 640.0) / -39.38
        return request

    def scale_box_to_pan_tilt(self, request):
        pan_angle = math.atan(request.x2 / 9.75)
        tilt_angle = (math.pi / 2) - math.acos(request.y2 / math.sqrt( request.x2 ** 2 + request.y2 **2 + 9.75**2))
        return pan_angle, tilt_angle

    def move_servos(self, pan_angle, tilt_angle):
        bottom_servo.ChangeDutyCycle(self.angle_to_pwm_pan(pan_angle))
        top_servo.ChangeDutyCycle(self.angle_to_pwm_pan(tilt_angle))
        return ""

    def angle_to_pwm_pan(self, angle):
        return 7.75 + (angle * -2.47)

    def angle_to_pwm_tilt(self, angle):
        return 7.75 + (angle * -2.47)

    def recenter(self):
        self.move_servos(0, 0)

    def TestPointReceiving(self, request, context):
        box_scaled = self.scale_ipad_to_box(request)
        pan_angle, tilt_angle = self.scale_box_to_pan_tilt(box_scaled)
        self.move_servos(pan_angle, tilt_angle)

        # self.mutex.acquire()
        # try:
        #     print('(' + str(request.x1) + ', ' + str(request.y1) + ') ----> ' + '(' + str(request.x2) + ', ' + str(request.y2) + ')')
        # finally:
        #     self.mutex.release()
        return grpc_pb2.GlowReply(message='Receieved!')

    def LotsOfPoints(self, request_iterator, context):
        for new_point in request_iterator:
            print('(' + str(new_point.x1) + ', ' + str(new_point.y1) + ') ----> ' + '(' + str(new_point.x2) + ', ' + str(new_point.y2))
        return grpc_pb2.GlowReply(message='Receieved!')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_pb2_grpc.add_GlowServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    laser_on()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        laser_off()
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
