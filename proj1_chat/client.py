import socket
import select
import sys
from utils import *

class chat_client():
    def __init__(self, name, host, port):
        self.name = name
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def send_msg(self, message):
        if len(message) < 200:
            message += ' '* (200-len(message))
        self.socket.send(message)

    def socket_connect(self):
        try :
            self.socket.connect((self.host, self.port))
        except :
            print(CLIENT_CANNOT_CONNECT.format(self.host, self.port))
            sys.exit()

    def start(self):
        self.socket_connect()
        self.send_msg(self.name)

        sys.stdout.write(CLIENT_MESSAGE_PREFIX)
        sys.stdout.flush()
        prefix = True

        msg_buffer = ''

        while True:
            ready_to_read, ready_to_write, in_error = select.select([sys.stdin, self.socket] , [], [])
            for s in ready_to_read:
                if s == self.socket:
                    data = self.socket.recv(MESSAGE_LENGTH)
                    #print(repr(data))
                    if not data:
                        print(CLIENT_SERVER_DISCONNECTED.format(self.host, self.port))
                        sys.exit()
                    else:
                        msg_buffer += data
                        if len(msg_buffer) >= 200:
                            if prefix:
                                sys.stdout.write(CLIENT_WIPE_ME + '\r')
                                prefix = False
                            msg_buffer = msg_buffer.strip()
                            if msg_buffer != '':
                                sys.stdout.write(msg_buffer + '\n')
                                sys.stdout.flush()
                            msg_buffer = ''
                else :
                    message = sys.stdin.readline()
                    self.send_msg(message)
                    prefix = False

            if prefix == False:
                sys.stdout.write(CLIENT_MESSAGE_PREFIX)
                sys.stdout.flush()
                prefix = True

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Please enter a server host address and port number."
        sys.exit()
    client = chat_client(sys.argv[1], sys.argv[2], sys.argv[3])
    client.start()
