from enum import Enum
from collections import namedtuple
import heapq

EventType = Enum("EventType", ["SendReady", "Receive"])
PacketType = Enum("PacketType", ["Data", "Ack"])

Stream = namedtuple("Stream", ["source", "destination", "window", "waiting"])
Packet = namedtuple("Packet", ["type", "source", "destination", "size"])
Event = namedtuple("Event", ["time", "type", "node", "packet"])

Node = namedtuple("Node", 
        ["routing", "streams", "speed", "delay", "queue", "busy", "log"])

Net = namedtuple("Net", ["nodes", "events"])

def init(speed, delay, routing):
    # todo generalize setup
    n = len(speed)
    print(n)
    nodes = [Node(routing[i], [], speed[i], delay[i], [[] for _ in range(n)], [False for _ in range(n)], []) for i in range(n)]
    nodes[0].streams.append(Stream(0, 1, 10, 0))
    init_events = [Event(EventType.SendReady, 0, i, None) for i in range(n)]
    heapq.heapify(init_events)
    return Net(
        nodes,
        init_events
    )

def step(net):
    event = heapq.heappop(net.events)
    node = net.nodes[event.node]
    if (event.type == EventType.SendReady):
        print("send", event)
        # queue any streams possible
        for stream in node.streams:
            while (stream.waiting < stream.window):
                # todo general packet size
                node.queue.append(Packet(PacketType.Data, event.node, stream.destination, 1024))
        # check packet queue
        if (len(node.queue) > 0):
            packet = node.queue.pop()
            # compute routing and delays
            nextNode = node.routing[packet.destination]
            propDelay = node.delay[nextNode]
            transmitDelay = packet.size / node.speed[nextNode]
            # send the packet (queue receive event)
            heapq.heappush(Event(event.time + propDelay + transmitDelay, EventType.Receive, nextNode, packet))
            # queue sendready
            heapq.heappush(Event(event.time + transmitDelay, EventType.SendReady, event.node, None))
    elif (event.type == EventType.Receive):
        print("receive", event)
        # compute routing and delays
        packet = Packet(PacketType.Ack, event.node, event.packet.source)
        # todo dedupe
        nextNode = node.routing[packet.destination]
        propDelay = node.delay[nextNode]
        # todo general ack size
        transmitDelay = packet.size / node.speed[nextNode]
        # queue the ack packet
        node.queue.append(packet)
        # restart sending if needed
        if (not(node.busy[nextNode])):
            heapq.heappush(Event(event.time, EventType.SendReady, event.node, None))
    else:
        raise Exception("Unknown event")
    return event
