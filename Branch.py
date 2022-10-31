from concurrent import futures
from time import sleep

import grpc

import bank_pb2
import bank_pb2_grpc


class Branch(bank_pb2_grpc.BankSystemServicer):

    def __init__(self, id, balance, branches, bindAddress):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branches = branches
        # the map of other branches
        # self.branchesMap = branchesMap
        # the bind address for this branch
        self.bindAddress = bindAddress
        # the list of Client stubs to communicate with the branches
        # self.stubList = list()
        # a list of received messages used for debugging purpose
        self.recvMsg = list()
        # iterate the processID of the branches


        # TODO: students are expected to store the processID of the branches
        pass

    # TODO: students are expected to process requests from both Client and Branch
    # def creatStub(self):
    #     return bank_pb2_grpc.BankSystemStub(grpc.insecure_channel(self.bindAddress))
    def MsgDelivery(self, request, context):
        if request.interface == "query":
            sleep(3)
            # print("Branch " + str(self.id) + " map: " + str(self.branchesMap))
            return bank_pb2.MsgDeliveryReply(
                interface="query", result="success", money=self.balance)
        elif request.interface == "deposit":
            return bank_pb2.MsgDeliveryReply(
                interface="deposit", result="success", money=self.deposit(request.money))
        elif request.interface == "withdraw":
            return bank_pb2.MsgDeliveryReply(
                interface="withdraw", result="success", money=self.withdraw(request.money))

    def deposit(self, money):
        self.balance += money
        return self.balance

    def withdraw(self, money):
        self.balance -= money
        return self.balance

    def updateBranchesMap(self, id, branch):
        self.branchesMap[id] = branch
        # print("Branch " + str(self.id) + " add new branch: " + "id - " + str(id) + " map - " + str(self.branchesMap))
