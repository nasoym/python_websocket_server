#!/usr/bin/env python
# from: http://sidekick.windforwings.com/2013/03/minimal-websocket-broadcast-server-in.html
 
import socket, hashlib, base64, threading
import json
import select
import asyncore

class WebsocketClient:
  #connection = None
  def __init__(self,connection,address):
    self.connection = connection
    self.address = address
    print ('connenction: ' + str(self.connection))
    print ('address: ' + str(self.address))

class PollingWebSocketServer:

  server_socket = None
  address = ''
  connected_clients = []

  def __init__(self,port=4545):
    self.port = port
    self.server_init()

  def server_init(self):
    if (self.server_socket == None):
      self.server_socket = socket.socket()
      self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.server_socket.setblocking(0)
      #server_socket.settimeout(1)
      self.server_socket.bind((self.address, self.port))
      self.server_socket.listen(5)

  def poll_connections(self):
    try:
      conn, addr = self.server_socket.accept()
      self.connected_clients.append(WebsocketClient(conn,addr))
    except socket.timeout, e:
      #print('socket timeout' + str(e))
      pass
    except socket.error, e:
      #print('socket error' + str(e))
      pass
  
  def hello(self):
    print('hello')
    print('port: ' + str(self.port))

t = PollingWebSocketServer()
t.hello()
while True:
  t.poll_connections()

# port = 4545
# server_socket = socket.socket()
# server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# server_socket.setblocking(0)
# #server_socket.settimeout(1)
# 
# server_socket.bind(('', port))
# server_socket.listen(5)
# 
# #while True:
# try:
#   print ('Waiting for connection...')
#   conn, addr = server_socket.accept()
#   print ('connenction: ' + str(conn))
#   print ('address: ' + str(addr))
# except socket.timeout, e:
#   print('socket timeout' + str(e))
# except socket.error, e:
#   print('socket error' + str(e))
# 
# #read_list = [server_socket]
# #while True:
# #    readable, writable, errored = select.select(read_list, [], [])
# #    print('.')
# #    for s in readable:
# #        if s is server_socket:
# #            client_socket, address = server_socket.accept()
# #            read_list.append(client_socket)
# #            print "Connection from", address
# #        else:
# #            data = s.recv(1024)
# #            if data:
# #                s.send(data)
# #            else:
# #                s.close()
# #                read_list.remove(s)
# #
