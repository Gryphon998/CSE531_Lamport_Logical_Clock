from concurrent import futures

import grpc

import bank_pb2
import bank_pb2_grpc


class Branch(bank_pb2_grpc.BankServicer):

    def __init__(self, id, balance, branches, bindAddress):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the bind address for this branch
        self.bindAddress = bindAddress
        # the list of Client stubs to communicate with the branches
        self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches

        # TODO: students are expected to store the processID of the branches
        pass

    # TODO: students are expected to process requests from both Client and Branch
    def MsgDelivery(self, request, context):
        pass

    def SayHello(self, request, context):
        return bank_pb2.HelloReply(message='Hello, %s!' % request.name)