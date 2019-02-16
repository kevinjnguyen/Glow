from concurrent import futures
import time
from threading import Thread, Lock
import logging

import grpc

import grpc_pb2
import grpc_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Greeter(grpc_pb2_grpc.GlowServicer):

    mutex = Lock()

    def scale_ipad_to_box(self, request):
        request.x1 = (request.x1 - 384.0) / 39.38
        request.x2 = (request.x2 - 384.0) / 39.38
        request.y1 = (request.y1 - 640.0) / -39.38
        request.y2 = (request.y2 - 640.0) / -39.38
        return request

    def scale_box_to_pan_tilt(self, request):
        return request

    def TestPointReceiving(self, request, context):
        box_scaled = self.scale_ipad_to_box(request)
        pan_tilt = self.scale_box_to_pan_tilt(box_scaled)

        self.mutex.acquire()
        try:
            print('(' + str(request.x1) + ', ' + str(request.y1) + ') ----> ' + '(' + str(request.x2) + ', ' + str(request.y2) + ')')
        finally:
            self.mutex.release()
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
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
