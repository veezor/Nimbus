#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import socket
import SocketServer
import BaseHTTPServer
import SimpleXMLRPCServer
from OpenSSL import SSL

import keymanager


class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,
                        SimpleXMLRPCServer.SimpleXMLRPCDispatcher,
                        SocketServer.ThreadingMixIn):

    def __init__(self, key_filename, cert_filename, server_address, logRequests=True):
        self.logRequests = logRequests

        SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        SocketServer.BaseServer.__init__(self, server_address, SecureXMLRpcRequestHandler)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file(key_filename)
        ctx.use_certificate_file(cert_filename)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()



class SecureXMLRpcRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):

    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, "rb", self.rbufsize)
        self.wfile = socket._fileobject(self.request, "wb", self.wbufsize)

    def do_POST(self):
        try:

            data = self.rfile.read(int(self.headers["content-length"]))
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
        except: # This should only happen if the module is buggy
            # internal error, report as HTTP server error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown() # Modified here!


def generate_keys(directory, prefix, ssl_config):
    key_manager = keymanager.KeyManager()
    key_manager.build_keys(ssl_config)
    key_manager.save_keys_on_directory(directory, prefix)


def secure_xmlrpc(key, certificate, server_address, ssl_config):
    """Creates key and certificate if necessary. Key and certificate must be same prefix and ends with .key and .cert.
          Returns a SecureXMLRPCServer object"""


    key_dir_name = os.path.dirname(key)
    cert_dir_name = os.path.dirname(certificate)

    if key_dir_name != cert_dir_name:
        raise ValueError("Key and Certificate dirname must be equals")

    if not key.endswith('.key') and not cert_dir_name.endswith('.cert'):
        raise ValueError('Key name must be ends with .key and Certificate name with .cert')

    if key.count('.') > 1 and cert_dir_name.count('.') > 1:
        raise ValueError('only one dot are allowed at key and certificate name')


    if not os.path.exists(key) and not os.path.exists(certificate):
        dirname = key_dir_name
        prefix = os.path.basename(key).split('.')[0]
        generate_keys(dirname, prefix, ssl_config)


    return SecureXMLRPCServer(key, certificate, server_address)