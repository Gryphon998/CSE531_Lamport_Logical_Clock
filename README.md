# Lamport Logical Clock

## Understanding Lamport's Logical Clock Algorithm
Lamport's logical clock algorithm, based on the concept of "Happened-before," defines a relationship between events. I perceive this relationship as a causal connection, represented by the "->" symbol. For instance, a->b signifies that event b is caused by event a.

An event a is recorded as a->b if any of the following conditions are met:

* Event a occurs before event b within the same process.
* Event a represents the sending of a message from one process, while event b represents the receiving of the same message by another process.

From a system perspective, the relative order of concurrent events is insignificant. The system only needs to distinguish events with a causal relationship. By maintaining this causal relationship, we can ensure that the entire distributed system is considered correct, at least logically. The sequencing of concurrent events without a causal relationship is of no concern.

Therefore, in our banking system, the order of two different events is not crucial. Instead, we focus on establishing the correct logical order for each event. For instance, in the case of customer deposits, the logical order would be: client -> branch -> propagated branch.

## Implementing Lamport's Logical Clock Algorithm
Having grasped the concept and significance of Lamport's logical clock algorithm in distributed systems, the next step is to implement this algorithm in our banking system. One critical aspect is understanding how the logical clock functions in distributed systems.

Initially, all client branches and customer branches should have a clock value of 0. When clients initiate events, multiple gRPC messages will circulate among the client branches. Determining how to increment the logical clock based on the logical order of events across the client branches becomes a key challenge.

## Printing the Output
Once the client branches complete all events, we must examine the interface and clock logs to ensure that events are executed in the correct logical order. However, in a distributed system where an event is distributed across multiple branches, it becomes challenging to extract and group events from different branches.

## Implementation
### Event_Request
``` python
def event_request(self, id, interface, clock):
  self.clock = max(self.clock, clock) + 1
  self.add_branch_log({"id": id, "name": interface + "_request", "clock": self.clock})
  self.add_event_log(id, {"clock": self.clock, "name": interface + "_request"})
```
This description is for the client branch responsible for receiving deposit or withdrawal requests from customers. The client branch follows a specific process: it compares the local clock time with the remote clock time provided in the received message and selects the larger value. Afterward, it increments the selected value by one.

### Event_Execute
``` python
def event_execute(self, id, interface):
 self.clock += 1
 self.add_branch_log({"id": id, "name": interface + "_execute", "clock": self.clock})
 self.add_event_log(id, {"clock": self.clock, "name": interface + "_execute"})
```
This description is also applicable to the client branch responsible for executing customers' requests. In this case, the client branch increments its local clock by one.

### Event_Response
``` python
def event_response(self, id, interface):
 self.clock += 1
 self.add_branch_log({"id": id, "name": interface + "_response", "clock": self.clock})
 self.add_event_log(id, {"clock": self.clock, "name": interface + "_response"})
```
This description pertains to the client branch, which provides an execute response to the client once all the propagate responses have been received from the branches. Additionally, the client branch increments its local clock by one. By combining these six functions, a logical clock can be created to record a logical timestamp for each process.

### Propagate_Request
``` python
def propagate_request(self, id, interface, clock):
 self.clock = max(self.clock, clock) + 1
 self.add_branch_log({"id": id, "name": interface + "_request", "clock": self.clock})
 self.add_event_log(id, {"clock": self.clock, "name": interface + "_request"})
```
This description pertains to the other branches, which receive propagate requests from the branch that has already executed customers' events. As part of their operation, these branches increment their local clocks by one.

### Propogate_Execute
``` python
def propagate_execute(self, id, interface):
 self.clock += 1
 self.add_branch_log({"id": id, "name": interface + "_execute", "clock": self.clock})
 self.add_event_log(id, {"clock": self.clock, "name": interface + "_execute"})
```
This description is also applicable to other branches responsible for executing propagate requests received from the branch that has already executed customers' events. As part of their process, these branches increment their local clocks by one.

### Propagate_Response
``` python
def propagate_response(self, id, interface, clock):
 self.clock = max(self.clock, clock) + 1
 self.add_branch_log({"id": id, "name": interface + "_response", "clock": self.clock})
 self.add_event_log(id, {"clock": self.clock, "name": interface + "_response"})
```
This description is for the client branch, which receives propagate responses from other client branches. In this process, the client branch compares the local clock time with the remote clock time provided in the received message and selects the larger value. Subsequently, it increments the selected value by one.

## Execution Command
```
python ./main.py input.json
```

##  Requirements
### Purpose
The goal of this project is to implement Lamport’s logical clock algorithm between Branches and Customers processes as shown in Diagram A.
<p align="center">
  <img src="https://github.com/Gryphon998/CSE531_Lamport_Logical_Clock/assets/41406456/7021d3a3-fda5-4bc5-96d5-717edf6eb0c5">
</p>

### Objectives
* Implement Lamport’s logical clock algorithm.
* Implement interconnected sub-interfaces in the correct location.
* Execute the specific order of interconnected sub-interfaces.
* Implement the six sub-interfaces (Event_Request, Event_Execute, Propagate_Request, Propogate_Execute, Propogate_Response, Event_Response) that updates the local clock of the Branch process and records the local clock of events.

### Description
Each event (Deposit and Withdraw) has a unique ID, and the sub-interfaces follow a specific order . The logical clock is required to maintain the happens-before order of the sub events that have the same unique ID, and of all the events on the same process. The table below and Diagram B describe how the logical clocks are expected to be processed within the subevents.

| Set Name  | Description |
| ------------- | ------------- |
| Event_Request  | This subevent happens when the Branch process receives a request from the Customer process. The Branch process selects the larger value between the local clock and the remote clock from the message, and increments one from the selected value.  |
| Event_Execute  | This subevent happens when the Branch process executes the event after the subevent “Event_Request”. The Branch process increments one from its local clock.  |
| Propagate_Request  | This subevent happens when the Branch process sends the propagation request to its fellow branch processes. The Branch process increments one from its local clock.  |
| Propogate_Execute  | This subevent happens when the Branch process executes the event after the subevent “Propogate_Request”. The Branch process increments one from its local clock.  |
| Propagate_Response  | This subevent happens when the Branch receives the result of the subevent “Propogate_Execute” from its fellow branches. The Branch process selects the biggest value between the local clock and the remote clock from the message, and increments one from the selected value.  |
| Event_Response  | This subevent happens after all the propagate responses are returned from the branches. The branch returns success / fail back to the Customer process. The Branch process increments one from its local clock. |

The Deposit and Withdraw events occur in four interfaces in the Branch.py. The students are expected to implement the subevents that will correctly record and update local clock of the Branch.py

<p align="center">
  <img src="https://github.com/Gryphon998/CSE531_Lamport_Logical_Clock/assets/41406456/7aa29e54-4a88-411d-91f5-5d7a1ba31ae6">
</p>

#### Branch to Customer interface
* Branch.Withdraw should invoke the Branch.Event_Request and Branch.Event_Execute. It then propagates the withdrawal request to the other branches. After all the propagation is executed, the branch invokes the Branch.Event_Response to the Customer process.
* Branch.Deposit should invoke the same order of sub-interfaces as the Branch.withdraw. Branch to

#### Branch to Branch Interface
* Branch.Withdraw_Propagate should invoke the Branch.Propagate_request and Branch.Propagate_Execute. The fellow branches will receive the propagation request and execute, and send back Branch.Propagate_Response accordingly.
* Branch.Deposit_Propagate should invoke the same order of sub-interfaces as the Branch.Withdraw_Propagate.

### Input and output
The input file contains a list of Customers and Branch processes. The format of the input file follows Project 1, but the output will be the recorded results from the Branch.py instead of the returned query results from the Customer.py. Note that the “id” parameter in the event is used to group the events together to identify the happen-before relationship.

#### Input format
```
[ // Start of the Array of Branch and Customer processes
 { // Customer process #1
  "id" : {a unique identifier of a customer or a branch},
  "type" : "customer",
  "events" : [{"interface":{query | deposit | withdraw}, "money": {an integer value},  "id": {unique identifier of an event}] 
 },
 { … }, // Customer process #2 
 { … }, // Customer process #3 
 { … }, // Customer process #N 
 { // Branch process #1 
 	"id" : {a unique identifier of a customer or a branch},
 	"type" : "branch",
 	"balance" : {replica of the amount of money stored in the branch}
 },
 { … }, // Branch process #2 
 { … }, // Branch process #3 
 { … }, // Branch process #N 
] // End of the Array of Branch and Customer processes
```

The output contains the list of logged results from the Branch process. The output will contain (1) the order of executed events of each branch process, and (2) the order of events of the same ID. Each of the results should follow the happens-before relationship.
#### Output format
```
[
 {
  "id" : {"a unique identifier of a branch"},
  "data" " [//a list of executed events in the branch]
 },
 {"…"}, // Branch process #2
 {"…"}, // Branch process #3
 {"…"}, // Branch process #N
 {
 { // A group of subevents with ID #1
  "eventid" : { a unique identifier of a event }
  "data" : [ a list of executed subevents ]
 }
 { … }, // Event #2
 { … }, // Event #3
 { … }, // Event #N
] // End of the Branch processes and the group of sub-events
```
