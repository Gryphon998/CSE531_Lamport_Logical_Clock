import grpc
from google.protobuf.json_format import MessageToDict
from time import sleep

import bank_pb2
import bank_pb2_grpc


class Branch(bank_pb2_grpc.BankSystemServicer):

    def __init__(self, id, balance, bind_address, branch_logger, event_logger):
        # unique ID of the branch
        self.id = id
        # balance of this branch
        self.balance = balance
        # the bind address for this branch
        self.bind_address = bind_address
        # the list of client stubs to communicate with this branch
        self.stubList = list()
        # set initial logical clock as 0
        self.clock = 0
        # branch logger to store this branch's activities
        self.branch_logger = branch_logger
        # event logger to store the events between this branch and its customers
        self.event_logger = event_logger

    def MsgDelivery(self, request, context):
        """
        Handle received messages from other branches or customers.
        :param request: a gRPC request from a branch or customer
        :param context: gRPC protocol required context
        """
        reply = None

        if request.interface == "query":
            # Handle "query" requests from customers
            reply = bank_pb2.MsgDeliveryReply(
                interface="query", result="success", money=self.balance,
                clock=self.clock)
        elif request.interface == "deposit":
            # Handle "deposit" requests from customers
            self.event_request(request.id, request.interface, request.clock)
            self.event_execute(request.id, request.interface)
            self.deposit(request.id, request.money, True)

            sleep(1)

            reply = bank_pb2.MsgDeliveryReply(
                interface="deposit", result="success", money=self.balance,
                clock=self.clock)

            self.event_response(request.id, request.interface)
        elif request.interface == "withdraw":
            # Handle "withdraw" requests from customers
            self.event_request(request.id, request.interface, request.clock)
            self.event_execute(request.id, request.interface)
            self.withdraw(request.id, request.money, True)

            sleep(1)

            reply = bank_pb2.MsgDeliveryReply(
                interface="withdraw", result="success", money=self.balance,
                clock=self.clock)

            self.event_response(request.id, request.interface)
        elif request.interface == "deposit_propagate":
            # Handle propagated "deposit" requests from other branches
            self.propagate_request(request.id, request.interface, request.clock)
            self.propagate_execute(request.id, request.interface)
            self.deposit(request.id, request.money, False)

            reply = bank_pb2.MsgDeliveryReply(
                interface=request.interface, result="success", money=self.balance,
                clock=self.clock)
        elif request.interface == "withdraw_propagate":
            # Handle propagated "withdraw" requests from other branches
            self.propagate_request(request.id, request.interface, request.clock)
            self.propagate_execute(request.id, request.interface)
            self.withdraw(request.id, request.money, False)

            reply = bank_pb2.MsgDeliveryReply(
                interface=request.interface, result="success", money=self.balance,
                clock=self.clock)

        return reply

    def deposit(self, id, money, propagate):
        """
        Deposit money for a customer and determine if propagate the message to other branches.
        :param id: customer id
        :param money: deposit money amount
        :param propagate: flag to control if propagate
        """
        self.balance += money

        if propagate:
            for stub in self.stubList:
                msg_reply = stub.MsgDelivery(bank_pb2.MsgDeliveryRequest(
                    id=id, interface="deposit_propagate", money=money, clock=self.clock))
                self.propagate_response(id, msg_reply.interface, msg_reply.clock)

    def withdraw(self, id, money, propagate):
        """
        Withdraw money for a customer and determine if propagate the message to other branches.
        :param id: customer id
        :param money: withdraw money amount
        :param propagate: flag to control if propagate
        """
        self.balance -= money

        if propagate:
            for stub in self.stubList:
                msg_reply = stub.MsgDelivery(bank_pb2.MsgDeliveryRequest(
                    id=id, interface="withdraw_propagate", money=money, clock=self.clock))
                self.propagate_response(id, msg_reply.interface, msg_reply.clock)

    def event_request(self, id, interface, clock):
        """
        Increase clock by 1 when receive a customer request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock = max(self.clock, clock) + 1
        self.add_branch_log({"id": id, "name": interface + "_request", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_request"})

    def event_execute(self, id, interface):
        """
        Increase clock by 1 when execute a customer request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock += 1
        self.add_branch_log({"id": id, "name": interface + "_execute", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_execute"})

    def event_response(self, id, interface):
        """
        Increase clock by 1 when response a customer request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock += 1
        self.add_branch_log({"id": id, "name": interface + "_response", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_response"})

    def propagate_request(self, id, interface, clock):
        """
        Increase clock by 1 when receive a propagated request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock = max(self.clock, clock) + 1
        self.add_branch_log({"id": id, "name": interface + "_request", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_request"})

    def propagate_execute(self, id, interface):
        """
        Increase clock by 1 when execute a propagated request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock += 1
        self.add_branch_log({"id": id, "name": interface + "_execute", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_execute"})

    def propagate_response(self, id, interface, clock):
        """
        Increase clock by 1 when response a propagated request
        :param id: request id
        :param interface: request type
        :param clock: current clock in the request
        """
        self.clock = max(self.clock, clock) + 1
        self.add_branch_log({"id": id, "name": interface + "_response", "clock": self.clock})
        self.add_event_log(id, {"clock": self.clock, "name": interface + "_response"})

    def add_stub(self, address):
        self.stubList.append(bank_pb2_grpc.BankSystemStub(grpc.insecure_channel(address)))

    def add_branch_log(self, log):
        if self.id not in self.branch_logger.keys():
            self.branch_logger[self.id] = [log]
        else:
            curr = self.branch_logger[self.id]
            curr.append(log)
            self.branch_logger[self.id] = curr

    def add_event_log(self, id, log):
        if id not in self.event_logger.keys():
            self.event_logger[id] = [log]
        else:
            curr = self.event_logger[id]
            curr.append(log)
            self.event_logger[id] = curr
