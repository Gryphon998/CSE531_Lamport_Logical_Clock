import grpc
import json
import logging
import multiprocessing
import socket
import sys
import time
from concurrent import futures

import bank_pb2_grpc
from Branch import Branch
from Customer import Customer

_LOGGER = logging.getLogger(__name__)
_PROCESS_COUNT = multiprocessing.cpu_count()
_THREAD_CONCURRENCY = _PROCESS_COUNT

address_map = {}
workers = []
branches = []


def _reserve_port():
    """Find a free port at localhost"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    return sock.getsockname()[1]


def _run_server(branch):
    """Start a branch serve in a subprocess with the passed in branch information."""
    _LOGGER.info("Initialize a new branch @ %s - id: %d, balance: %d.", branch.bind_address, branch.id,
                 branch.balance)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_THREAD_CONCURRENCY))
    bank_pb2_grpc.add_BankSystemServicer_to_server(branch, server)
    server.add_insecure_port(branch.bind_address)
    server.start()
    server.wait_for_termination()


def _run_client(customer):
    """Start a customer serve with the passed in customer information."""
    _LOGGER.info("Initialize a new customer - id: %d.", customer.id)

    customer.executeEvents()


def _log_output(branch_logger, event_logger):
    """Store every branch's branch and event logs into 'output.log' file."""
    time.sleep(5)
    output = list()

    for pid, data in branch_logger.items():
        branch_log = dict()
        branch_log["pid"] = pid
        branch_log["data"] = data
        output.append(branch_log)

    for id, data in event_logger.items():
        event_log = dict()
        event_log["eventid"] = id
        event_log["data"] = data
        output.append(event_log)

    _LOGGER.info(output)

    with open('output.log', 'w+') as fp:
        dump_str = json.dumps(output, indent=2)
        print(dump_str, file=fp)

    fp.close()


def branches_init(processes, branch_logger, event_logger):
    """
    Init branches based on the information of input json.
    :param processes: processes recorded in json file
    :param branch_logger: a logger to log all the branch activities
    :param event_logger: a logger to log all the events between branch and customer
    """
    for process in processes:
        if process["type"] == "branch":
            new_branch = Branch(process["id"], process["balance"], 'localhost:{}'.format(_reserve_port()),
                                branch_logger, event_logger)
            address_map[new_branch.id] = new_branch.bind_address
            branches.append(new_branch)

    # Add all other branches' addresses to a branch.
    for branch in branches:
        for id, address in address_map.items():
            if branch.id != id:
                branch.add_stub(address)

        worker = multiprocessing.Process(target=_run_server,
                                         args=(branch,))
        worker.start()
        workers.append(worker)


def customer_init(processes):
    """
    Init customers based on the information of input json.
    :param processes: processes recorded in json file
    """
    for process in processes:
        if process["type"] == "customer":
            new_customer = Customer(process["id"], process["events"], address_map.get(process["id"]))
            worker = multiprocessing.Process(target=_run_client,
                                             args=(new_customer,))
            worker.start()
            workers.append(worker)


if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[PID %(process)d] %(message)s')
    handler.setFormatter(formatter)
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(logging.INFO)
    f = open(sys.argv[1])
    input_json = json.load(f)

    manager = multiprocessing.Manager()
    branch_logger = manager.dict()
    event_logger = manager.dict()

    # Parse input json to initialize branches and customers with 1 second interval.
    branches_init(input_json, branch_logger, event_logger)
    time.sleep(1)
    customer_init(input_json)

    # Start a new thread to store log to output.log
    worker = multiprocessing.Process(target=_log_output, args=(branch_logger, event_logger))
    worker.start()
    workers.append(worker)

    for worker in workers:
        worker.join()

    f.close()
