from concurrent import futures
import time
import logging

import grpc

import grpc_pb2
import grpc_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Greeter(grpc_pb2_grpc.GlowServicer):

    def TestPointReceiving(self, request, context) :
        print('Received: (' + str(request.x) + ', ' + str(request.y) + ')')
        return grpc_pb2.GlowReply(message='Receieved!')

    def LotsOfPoints(self, request_iterator, context):
        for new_point in request_iterator:
            print('Received: (' + str(new_point.x) + ', ' + str(new_point.y) + ')')
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
