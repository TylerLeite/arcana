import http.server
import socketserver

import json

from spell import *

class RESTHandler(http.server.BaseHTTPRequestHandler):
  def get_body (self):
    length = int(self.headers.get_all('Content-Length')[0])
    binary = self.rfile.read(length)
    return json.loads(binary.decode())

  def do_POST(self):
    body = self.get_body()

    s = Spell()
    print(body["words"].split(' '))
    s.compile(body["words"].split(' '))
    res = json.dumps(s.json_data(body["words"].split(' ')))

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Expose-Headers", "Access-Control-Allow-Origin")
    self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")
    self.end_headers()
    self.wfile.write(bytes(res, "utf-8"))


PORT = 20394
Handler = RESTHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
  print ("Server started on port", PORT)
  httpd.serve_forever()

