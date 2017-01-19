import socket
import sys
client_socket = socket.socket()
client_socket.connect((sys.argv[1], int(sys.argv[2])))
client_socket.send(raw_input())
