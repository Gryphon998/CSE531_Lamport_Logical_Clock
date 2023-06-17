import grpc
from time import sleep
from google.protobuf.json_format import MessageToDict

import bank_pb2
import bank_pb2_grpc


class Customer:
    def __init__(self, id, events, address):
        # unique ID of the Customer
        self.id = id
        # events from the input json
        self.events = events
        # pointer for the stub
        self.stub = self.createStub(address)
        # set initial logical clock as 0
        self.clock = 0

    def createStub(self, address):
        return bank_pb2_grpc.BankSystemStub(grpc.insecure_channel(address))

    def executeEvents(self):
        """Execute the event from input json and increase the clock by 1."""
        for event in self.events:
            id = event["id"]
            interface = event["interface"]
            money = event["money"]
            clock = self.clock
            if interface != "query":
                clock += 1
            else:
                sleep(3)

            msg = MessageToDict(self.stub.MsgDelivery(
                bank_pb2.MsgDeliveryRequest(id=id, interface=interface, money=money, clock=clock)))

            if interface == "deposit" or interface == "withdraw":
                del msg['money']
