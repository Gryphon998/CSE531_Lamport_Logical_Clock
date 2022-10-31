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
        # self.targetBranchAddress = targetBranchStub
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # pointer for the stub
        self.stub = self.createStub(address)

    # TODO: students are expected to create the Customer stub
    def createStub(self, address):
        return bank_pb2_grpc.BankSystemStub(grpc.insecure_channel(address))

    # TODO: students are expected to send out the events to the Bank
    def executeEvents(self):
        for event in self.events:
            id = event["id"]
            interface = event["interface"]
            money = event["money"]
            print(self.stub.MsgDelivery(bank_pb2.MsgDeliveryRequest(id=id, interface=interface, money=money)))
