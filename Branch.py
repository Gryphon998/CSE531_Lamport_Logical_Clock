import logging
import sys
from time import sleep

import grpc
from google.protobuf.json_format import MessageToDict

import bank_pb2
import bank_pb2_grpc


class Branch(bank_pb2_grpc.BankSystemServicer):

    def __init__(self, id, balance, branches, bindAddress, clock, logger):
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
        # logger
        self.logger = logger
        self.clock = clock

        # iterate the processID of the branches
        # TODO: students are expected to store the processID of the branches
        pass

    # TODO: students are expected to process requests from both Client and Branch
    def MsgDelivery(self, request, context):
        reply = None

        if request.interface == "query":
            sleep(3)
            self.logger.info({"pid": self.id, "data": self.recvMsg})
            reply = bank_pb2.MsgDeliveryReply(
                interface="query", result="success", money=self.balance,
                clock=self.clock)

        elif request.interface == "deposit":
            self.event_request(request.id, request.interface, request.clock)

            self.event_execute(request.id, request.interface, self.clock)
            self.deposit(request.id, request.money, True)

            reply = bank_pb2.MsgDeliveryReply(
                interface="deposit", result="success", money=self.balance,
                clock=self.clock)

            self.event_response(request.id, request.interface, self.clock)

        elif request.interface == "withdraw":
            self.event_request(request.id, request.interface, request.clock)

            self.event_execute(request.id, request.interface, self.clock)
            self.withdraw(request.id, request.money, True)

            reply = bank_pb2.MsgDeliveryReply(
                interface="withdraw", result="success", money=self.balance,
                clock=self.clock)

            self.event_response(request.id, request.interface, self.clock)

        elif request.interface == "deposit_propagate":
            sleep(1)
            self.propagate_request(request.id, request.interface, request.clock)
            self.propagate_execute(request.id, request.interface, self.clock)
            self.deposit(request.id, request.money, False)

            reply = bank_pb2.MsgDeliveryReply(
                interface=request.interface, result="success", money=self.balance,
                clock=self.clock)

        elif request.interface == "withdraw_propagate":
            sleep(1)
            self.propagate_request(request.id, request.interface, request.clock)
            self.propagate_execute(request.id, request.interface, self.clock)
            self.withdraw(request.id, request.money, False)

            reply = bank_pb2.MsgDeliveryReply(
                interface=request.interface, result="success", money=self.balance,
                clock=self.clock)

        return reply

    def deposit(self, id, money, propagate):
        self.balance += money

        if propagate:
            for stub in self.stubList:
                msg_reply = stub.MsgDelivery(bank_pb2.MsgDeliveryRequest(
                    id=id, interface="deposit_propagate", money=money, clock=self.clock))
                self.propagate_response(id, msg_reply.interface, msg_reply.clock)

    def withdraw(self, id, money, propagate):
        self.balance -= money

        if propagate:
            for stub in self.stubList:
                msg_reply = stub.MsgDelivery(bank_pb2.MsgDeliveryRequest(
                    id=id, interface="withdraw_propagate", money=money, clock=self.clock))
                self.propagate_response(id, msg_reply.interface, msg_reply.clock)

    def event_request(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_request", "clock": self.clock})

    def event_execute(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_execute", "clock": self.clock})

    def propagate_request(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_request", "clock": self.clock})

    def propagate_execute(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_execute", "clock": self.clock})

    def propagate_response(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_response", "clock": self.clock})

    def event_response(self, id, interface, clock):
        self.clock = max(self.clock, clock) + 1
        self.recvMsg.append({"id": id, "name": interface + "_response", "clock": self.clock})

    def add_stub(self, address):
        self.stubList.append(bank_pb2_grpc.BankSystemStub(grpc.insecure_channel(address)))
