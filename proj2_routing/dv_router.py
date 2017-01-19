"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.dv_table = {} # {dst :[cost,port,last_updated_time]}
        self.port_table = {} #{port: latency}

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.port_table[port] = latency
        for d in self.dv_table.keys():
            self.send(basics.RoutePacket(d,self.dv_table[d][0]), port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        tmp = []
        if port in self.port_table.keys():
            del self.port_table[port]
        for dst in self.dv_table.keys():
            if self.dv_table[dst][1] == port:
                tmp.append(dst)
        if self.POISON_MODE:
            for t in tmp:
                self.send(basics.RoutePacket(t, INFINITY), flood = True) #route poisoning
                del self.dv_table[t] 
        else:
            for t in tmp:
                del self.dv_table[t]
            for dst in self.dv_table.keys():
                self.send(basics.RoutePacket(dst, self.dv_table[dst][0]), flood = True)

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """
        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            dst = packet.destination
            cost = packet.latency
            if self.POISON_MODE and cost == INFINITY: #route poisoning and poison reverse
                for available_dst in self.dv_table.keys():
                    if self.dv_table[available_dst][1] == port:
                        self.send(basics.RoutePacket(available_dst, INFINITY), port)
                        del self.dv_table[available_dst]

            if dst not in self.dv_table.keys():
                if cost != INFINITY: 
                    self.dv_table[dst] = [self.port_table[port] + cost,port, 0]
                    self.send(basics.RoutePacket(dst, self.dv_table[dst][0]), port, flood = True)

            else: 
                if self.port_table[port] + cost < self.dv_table[dst][0]:
                    self.dv_table[dst] = [self.port_table[port] + cost,port, 0]
                    self.send(basics.RoutePacket(dst, self.dv_table[dst][0]), port, flood = True)
                if self.dv_table[dst][1] == port and  cost + self.port_table[port] > self.dv_table[dst][0]:
                    new_cost = cost + self.port_table[port]
                    self.dv_table[dst] = [cost + self.port_table[port],port, 0]
                    self.send(basics.RoutePacket(dst, self.dv_table[dst][0]), port, flood = True)
                if self.port_table[port] + cost == self.dv_table[dst][0]:
                    self.dv_table[dst][2] = 0

        elif isinstance(packet, basics.HostDiscoveryPacket):
            self.dv_table[packet.src] = [self.port_table[port], port, 0]
            for available_dst in self.dv_table.keys():
                self.send(basics.RoutePacket(available_dst, self.dv_table[available_dst][0]), port, flood = True)
        else:
            if packet.dst in self.dv_table.keys() and self.dv_table[packet.dst][1] != port:
                self.send(packet, self.dv_table[packet.dst][1])




    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        expired_entries = []
        for dst in self.dv_table.keys():
            self.dv_table[dst][2] += self.DEFAULT_TIMER_INTERVAL
            if self.dv_table[dst][2] >= self.ROUTE_TIMEOUT:
                expired_entries.append(dst)
        for e in expired_entries:
            if self.port_table[self.dv_table[e][1]] == self.dv_table[e][0] and self.dv_table[e][1] in self.port_table.keys():
                self.dv_table[e][2] = 0
            else:
                del self.dv_table[e]

        for dst in self.dv_table.keys():
            self.send(basics.RoutePacket(dst, self.dv_table[dst][0]), self.dv_table[dst][1], flood = True)


