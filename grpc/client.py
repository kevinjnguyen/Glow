from __future__ import print_function
import logging

import grpc

import grpc_pb2
import grpc_pb2_grpc

def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('192.168.43.144:50051') as channel:
        stub = grpc_pb2_grpc.GlowStub(channel)
        response = stub.TestPointReceiving(grpc_pb2.PointRequest(x=1,y=2))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()