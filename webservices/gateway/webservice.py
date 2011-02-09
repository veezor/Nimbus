import sys
import os
import socket
import logging
from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer

os.environ['DJANGO_SETTINGS_MODULE'] = 'gateway.settings'

from django.contrib.auth.models import User


logger = logging.getLogger(__name__)


(ADDRESS, PORT) = ("127.0.0.1", 10000)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


class GatewayAdminService(object):

    def create_user(self, username, password):
        user = User(username=username)
        user.set_password(password)
        user.save()


    def block_user(self, username):
        user = User.objects.get(username=username, is_active=True)
        user.is_active = False
        user.save()

    def unblock_user(self, username):
        user = User.objects.get(username=username, is_active=False)
        user.is_active = True
        user.save()


    def run(self):
        try:
            self.server = ThreadedXMLRPCServer(( ADDRESS, PORT ), allow_none=True)
            self.server.register_instance(self)
            logger.info( "Initializing GatewayAdminService" )
            self.server.serve_forever()
        except socket.error, e:
            logger.error( "GatewayAdminService not initialized." )
            sys.exit(1)


def main():
    service = GatewayAdminService()
    service.run()


if __name__ == "__main__":
    main()