import grpc

import bank_pb2
import bank_pb2_grpc


class Customer:
    def __init__(self, id, events, address):
        # unique ID of the Customer
        self.id = id
        # events from the input
        self.events = events
        # target branch bind address
        self.targetBranchAddress = address
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = self.createStub()

    # TODO: students are expected to create the Customer stub
    def createStub(self):
        return bank_pb2_grpc.BankStub(grpc.insecure_channel(self.targetBranchAddress))

    # TODO: students are expected to send out the events to the Bank
    def executeEvents(self):
        print(self.stub.SayHello(bank_pb2.HelloRequest(name='customer ' + str(self.id))))