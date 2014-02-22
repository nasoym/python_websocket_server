#!/usr/bin/env python
# from: http://sidekick.windforwings.com/2013/03/minimal-websocket-broadcast-server-in.html
 
import socket, hashlib, base64, threading
import json
#import select
#import asyncore

import errno

class WebsocketClient:
  MAGIC = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
  HSHAKE_RESP = "HTTP/1.1 101 Switching Protocols\r\n" + \
              "Upgrade: websocket\r\n" + \
              "Connection: Upgrade\r\n" + \
              "Sec-WebSocket-Accept: %s\r\n" + \
              "\r\n"

  def __init__(self,connection,address):
    self.connection = connection
    self.address = address
    self.handshaked = False

  def serve_connection(self):
    if (self.handshaked == False):
      self.handshaked = self.handshake()
      return True
    else:
      return self.poll_message()

  def poll_message(self):
    try:
      data = self.recv_data()
      print("received: %s" % (data,))
      #self.broadcast_resp(data)
      return True
    except socket.error, e:
      if e.errno == errno.EAGAIN:
        #print('errno.EAGAIN')
        pass
      else:
        print('socket error' + str(e))
      pass
    except Exception as e:
      pass
      print("Exception %s" % (str(e)))
      return False

  def recv_data(self):
    # as a simple server, we expect to receive:
    #    - all data at one go and one frame
    #    - one frame at a time
    #    - text protocol
    #    - no ping pong messages
    data = bytearray(self.connection.recv(512))
    if(len(data) < 6):
      raise Exception("Error reading data")
    # FIN bit must be set to indicate end of frame
    assert(0x1 == (0xFF & data[0]) >> 7)
    # data must be a text frame
    # 0x8 (close connection) is handled with assertion failure
    assert(0x1 == (0xF & data[0]))
    # assert that data is masked
    assert(0x1 == (0xFF & data[1]) >> 7)
    datalen = (0x7F & data[1])
    #print("received data len %d" %(datalen,))
    str_data = ''
    if(datalen > 0):
      mask_key = data[2:6]
      masked_data = data[6:(6+datalen)]
      unmasked_data = [masked_data[i] ^ mask_key[i%4] for i in range(len(masked_data))]
      str_data = str(bytearray(unmasked_data))
    return str_data

  def parse_headers (self, data):
    headers = {}
    lines = data.splitlines()
    for l in lines:
        parts = l.split(": ", 1)
        if len(parts) == 2:
            headers[parts[0]] = parts[1]
    headers['code'] = lines[len(lines) - 1]
    return headers

  def handshake (self):
    try:
      data = self.connection.recv(2048)
      #print('Handshaking...')
      headers = self.parse_headers(data)
      #print('Got headers:')
      #for k, v in headers.iteritems():
      #    print k, ':', v
      key = headers['Sec-WebSocket-Key']
      resp_data = self.HSHAKE_RESP % ((base64.b64encode(hashlib.sha1(key+self.MAGIC).digest()),))
      #print('Response: [%s]' % (resp_data,))
      #return self.connection.send(resp_data)
      print('Handshaked')
      self.connection.send(resp_data)
      return True
    except socket.error, e:
      pass
    return False

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

    connections_to_remove = []
    for c in self.connected_clients:
      if (c.serve_connection() == False):
        connections_to_remove.append(c)
    for c in connections_to_remove:
      self.connected_clients.remove(c)

  
t = PollingWebSocketServer()
while True:
  t.poll_connections()

