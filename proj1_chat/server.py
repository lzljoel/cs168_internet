import socket
import select
import sys 
from utils import *

class chat_server():

    command_arg_config = {
        'join': (1, SERVER_JOIN_REQUIRES_ARGUMENT),
        'create': (1, SERVER_CREATE_REQUIRES_ARGUMENT),
        'list':(0, '')
    }

    def __init__(self, host, port):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.socket_buffer = {}
        self.socket_list = [self.socket]
        self.client_name = {}
        self.client_channel = {}
        self.channels = {}

    def start_server(self):
        while True:
            ready_to_read,ready_to_write,in_error = select.select(self.socket_list,[],[])
            for client in ready_to_read:
                if client == self.socket:
                    sock, address = client.accept()
                    self.socket_list.append(sock)
                else:
                    try:
                        data = client.recv(MESSAGE_LENGTH)
                        if data:
                            self.write_buffer(client, data)
                            if self.has_buffer(client):
                                self.read_buffer(client)
                            #print(client, data, len(data))
                        else:
                            if client in self.socket_list:
                                self.socket_list.remove(client)
                            self.leave_channel(client)
                    except:
                        self.channel_broadcast(self.client_channel[client], client, "\r" + SERVER_CLIENT_LEFT_CHANNEL.format(self.get_client_name(client)) + '\n')
                        continue
            


    def get_client_name(self, client):
        if client not in self.client_name:
            return ''
        return self.client_name[client]

    def channel_broadcast(self, channel, from_socket, message):
        for socket in self.channels[channel]:
            if socket != self.socket and socket != from_socket:
                try :
                    self.server_send(socket, message)
                except :
                    socket.close()
                    if socket in self.socket_list:
                        self.socket_list.remove(socket)

    def server_send(self, socket, message):
        try :
            if len(message) < 200:
                message += ' '*(200-len(message))
            # print 'SEND:', socket, repr(message)
            socket.send(message)
        except :
            socket.close()
            if socket in self.socket_list:
                self.socket_list.remove(socket)

    def command_check(self, command, argument):
        try:
            if len(argument) != self.command_arg_config[command][0]:
                return (False, self.command_arg_config[command][1])
        except:
            return (False, SERVER_INVALID_CONTROL_MESSAGE.format(command))
        return (True, '')

    def has_buffer(self, sock):
        return len(self.socket_buffer[sock]) >= 200
    
    def write_buffer(self, socket, data):
        if socket in self.socket_buffer:
            self.socket_buffer[socket] += data
        else:
            self.socket_buffer[socket] = data

    def read_buffer(self, sock):
        message = self.socket_buffer[sock].strip()
        #print 'READ:', sock, message         
        if message.startswith('/'):
            message = message.split()
            msg_type = message[0][1:]
            argument = message[1:]

            is_valid, error_msg = self.command_check(msg_type, argument)
            if not is_valid:
                self.send_announcement(sock, error_msg)
                del self.socket_buffer[sock]
                return

            argument = ' '.join(argument)
            if msg_type == 'join':
                self.join_channel(sock, argument)
            elif msg_type == 'create':
                self.create_channel(sock, argument)
            elif msg_type == 'list':
                self.get_channel_list(sock)
        else:
            if sock not in self.client_name:
                self.client_name[sock] = message
            else:
                self.send_msg(sock, message)

        del self.socket_buffer[sock]


    def send_msg(self, client, msg):
        if client in self.client_channel:
            self.channel_broadcast(self.client_channel[client], client, "[{0}] {1}".format(self.get_client_name(client), msg))
        else:
            self.send_announcement(client, SERVER_CLIENT_NOT_IN_CHANNEL)

    def create_channel(self, client, channel):
        if channel in self.channels:
            self.send_announcement(client, SERVER_CHANNEL_EXISTS.format(channel))
        else:
            self.channels[channel] = []
            self.join_channel(client, channel)

    def join_channel(self, client, channel):
        if channel not in self.channels:
            self.send_announcement(client, SERVER_NO_CHANNEL_EXISTS.format(channel)) 
        else:
            self.leave_channel(client)
            self.client_channel[client] = channel
            self.channel_broadcast(self.client_channel[client], client, SERVER_CLIENT_JOINED_CHANNEL.format(self.get_client_name(client)) + '\n')
            self.channels[channel].append(client)
   
    def leave_channel(self, client):
        if client in self.client_channel:
            self.channels[self.client_channel[client]].remove(client)
            self.channel_broadcast(self.client_channel[client], client, SERVER_CLIENT_LEFT_CHANNEL.format(self.get_client_name(client)) + '\n')
            del self.client_channel[client]

    def get_channel_list(self, client):
        self.send_announcement(client, '\n'.join(self.channels.keys()))

    def send_announcement(self, client, announcement):
        self.server_send(client, announcement)

        
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Please enter a port number."
        sys.exit()
    server = chat_server("localhost", sys.argv[1])
    server.start_server()





