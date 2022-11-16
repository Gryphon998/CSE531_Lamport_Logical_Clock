import json
import logging
import multiprocessing
import sys
import socket
import time

import bank_pb2_grpc

from concurrent import futures

import grpc

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
    """Start a server in a subprocess."""
    _LOGGER.info("Initialize new branch @ %s: id - %d, balance - %d ", branch.bindAddress, branch.id,
                 branch.balance)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=_THREAD_CONCURRENCY))
    bank_pb2_grpc.add_BankSystemServicer_to_server(branch, server)
    server.add_insecure_port(branch.bindAddress)
    server.start()
    server.wait_for_termination()


def _run_client(customer):
    customer.executeEvents()


def _log_output(branch_logger, event_logger):
    time.sleep(5)
    output = list()

    for k, v in branch_logger.items():
        d = dict()
        d["pid"] = k
        d["data"] = v
        output.append(d)

    for k, v in event_logger.items():
        d = dict()
        d["eventid"] = k
        d["data"] = v
        output.append(d)

    _LOGGER.info(output)

    with open('output.log', 'w+') as fp:
        dump_str = json.dumps(output, indent=2)
        print(dump_str, file=fp)

    fp.close()


def branches_init(processes, branch_logger, event_logger):
    for p in processes:
        if p["type"] == "branch":
            new_branch = Branch(p["id"], p["balance"], [], 'localhost:{}'.format(_reserve_port()), branch_logger, event_logger)
            address_map[new_branch.id] = new_branch.bindAddress
            branches.append(new_branch)

    for b in branches:
        for k, v in address_map.items():
            if b.id != k:
                b.add_stub(v)

        worker = multiprocessing.Process(target=_run_server,
                                         args=(b,))
        worker.start()
        workers.append(worker)


def customer_init(processes):
    for p in processes:
        if p["type"] == "customer":
            new_customer = Customer(p["id"], p["events"], address_map.get(p["id"]))
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

    # Parse input json to initialize branches
    branches_init(input_json, branch_logger, event_logger)
    time.sleep(1)
    customer_init(input_json)

    # Print log to output.log
    worker = multiprocessing.Process(target=_log_output, args=(branch_logger, event_logger))
    worker.start()
    workers.append(worker)

    for worker in workers:
        worker.join()

    f.close()
