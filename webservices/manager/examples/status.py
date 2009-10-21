from SOAPpy import SOAPProxy
server = SOAPProxy("http://127.0.0.1:8888")
print server.status_director()
