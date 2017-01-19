import socket
import sys
server_socket = socket.socket()
server_socket.bind(('localhost', int(sys.argv[1])))
server_socket.listen(5)
(new_sock, address) = server_socket.accept()
data = new_sock.recv(200)
print data