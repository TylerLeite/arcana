import http.server
import socketserver

import json

from spell import *

class RESTHandler(http.server.BaseHTTPRequestHandler):
  def get_body (self):
    length = int(self.headers.get_all('Content-Length')[0])
    binary = self.rfile.read(length)
    return json.loads(binary.decode())

  def default_headers(self):
    self.send_header("Content-Type", "application/json")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
    self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")

  def do_POST(self):
    print(self.path)

    res = None
    if self.path == '/compile':
      res = self.do_POST_compile()

    self.send_response(200)
    self.default_headers()
    self.end_headers()
    self.wfile.write(bytes(res, "utf-8"))

  def do_POST_compile(self):
    body = self.get_body()

    s = Spell()
    s.compile(body["words"].split(' '))
    res = json.dumps(s.json_data(body["words"].split(' ')))
    return res

  def do_GET(self):
    print(self.path)
    res = None
    if self.path == '/tokens':
      res = self.do_GET_tokens()

    self.send_response(200)
    self.default_headers()
    self.end_headers()
    self.wfile.write(bytes(res, "utf-8"))

  def do_GET_tokens(self):
    out = ''
    with open('tokens.json', 'r') as file:
      for line in file:
        out += line + '\n'
    return out

PORT = 20394
Handler = RESTHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
  print ("Server started on port", PORT)
  httpd.serve_forever()

