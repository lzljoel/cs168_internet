import wan_optimizer
import utils
import tcp_packet

class WanOptimizer(wan_optimizer.BaseWanOptimizer):
    """ WAN Optimizer that divides data into fixed-size blocks.

    This WAN optimizer should implement part 1 of project 4.
    """

    # Size of blocks to store, and send only the hash when the block has been
    # sent previously
    BLOCK_SIZE = 8000

    def __init__(self):
        wan_optimizer.BaseWanOptimizer.__init__(self)
        # Add any code that you like here (but do not add any constructor arguments).
        self.hash_map = {}
        self.block_buffer = {}
        return

    def receive(self, packet):
        """ Handles receiving a packet.

        Right now, this function simply forwards packets to clients (if a packet
        is destined to one of the directly connected clients), or otherwise sends
        packets across the WAN. You should change this function to implement the
        functionality described in part 1.  You are welcome to implement private
        helper fuctions that you call here. You should *not* be calling any functions
        or directly accessing any variables in the other middlebox on the other side of 
        the WAN; this WAN optimizer should operate based only on its own local state
        and packets that have been received.
        """
        if packet.dest in self.address_to_port:
            # The packet is destined to one of the clients connected to this middlebox;
            # send the packet there.
            # Always send raw data to clients.
            if packet.is_raw_data:
            # The packet contains raw data
                block_key = (packet.src, packet.dest)
                if block_key not in self.block_buffer:
                    self.block_buffer[block_key] = ""
                self.block_buffer[block_key] += packet.payload
                if packet.is_fin or (len(self.block_buffer[block_key]) >= self.BLOCK_SIZE):
                    if self.block_buffer[block_key] <= self.BLOCK_SIZE:
                        real_data = self.block_buffer[block_key]
                        self.block_buffer[block_key] = ""
                    else:
                        real_data = self.block_buffer[block_key][:self.BLOCK_SIZE]
                        self.block_buffer[block_key] = self.block_buffer[block_key][self.BLOCK_SIZE:]

                    if utils.get_hash(real_data) not in self.hash_map:
                        self.hash_map[utils.get_hash(real_data)] = real_data
                    num_packets = int((len(real_data)-1)/1500)
                    for i in range(num_packets):
                        raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, False, real_data[1500*i:1500*(i+1)])
                        self.send(raw_packet,self.address_to_port[packet.dest])
                    raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, packet.is_fin, real_data[1500*(int((len(real_data)-1)/1500)):])
                    self.send(raw_packet, self.address_to_port[packet.dest])
                            
            else:
                raw_data = self.hash_map[packet.payload]
                num_packets = int((len(raw_data)-1)/1500)
                for i in range(num_packets):
                    raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, False, raw_data[1500*i:1500*(i+1)])
                    self.send(raw_packet,self.address_to_port[packet.dest])
                raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, packet.is_fin, raw_data[1500*(int((len(raw_data)-1)/1500)):])
                self.send(raw_packet, self.address_to_port[packet.dest])
        else:
            # The packet must be destined to a host connected to the other middlebox
            # so send it across the WAN.
            if packet.is_raw_data:
                block_key = (packet.src, packet.dest)
                if block_key not in self.block_buffer:
                    self.block_buffer[block_key] = ""
                self.block_buffer[block_key] += packet.payload
                if packet.is_fin or (len(self.block_buffer[block_key]) >= self.BLOCK_SIZE):
                    if self.block_buffer[block_key] <= self.BLOCK_SIZE:
                        real_data = self.block_buffer[block_key]
                        self.block_buffer[block_key] = ""
                    else:
                        real_data = self.block_buffer[block_key][:self.BLOCK_SIZE]
                        self.block_buffer[block_key] = self.block_buffer[block_key][self.BLOCK_SIZE:]

                    if utils.get_hash(real_data) not in self.hash_map:
                        self.hash_map[utils.get_hash(real_data)] = real_data
                        num_packets = int((len(real_data)-1)/1500)
                        for i in range(num_packets):
                            raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, False, real_data[1500*i:1500*(i+1)])
                            self.send(raw_packet,self.wan_port)
                        raw_packet = tcp_packet.Packet(packet.src, packet.dest, True, packet.is_fin, real_data[1500*(int((len(real_data)-1)/1500)):])
                        self.send(raw_packet, self.wan_port)
                    else:
                        new_packet = tcp_packet.Packet(packet.src, packet.dest, False, packet.is_fin, utils.get_hash(real_data))
                        self.send(new_packet, self.wan_port)

            else:
                self.send(packet, self.wan_port)


