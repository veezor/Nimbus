from SOAPpy import SOAPProxy
server = SOAPProxy("http://127.0.0.1:8888")
server.generate_iftab("rede1","00:00:00:00:00:00")
