import md5
import hmac
import base64
import struct
import socket
import random
import time



DEBUG = False


def _generate_challenge():
    random.seed(time.time())
    first = int(random.random() * 10**6)
    second = int(time.time())
    hostname = socket.gethostname()
    return "<%s.%s@%s>" % (first, second, hostname)




class BSocket(object):


    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.authenticated = False


    def connect(self, address, port):
        self.socket.connect((address, port))


    def close(self):
        self.socket.close()


    def _bacula_encode(self, msg):
        code = struct.pack("!i", len(msg))
        return code + msg

    def _bacula_decode(self, datasize):
        datasize = struct.unpack("!i", datasize)[0]
        return datasize


    def bsend_message_control(self, code):
        msg = struct.pack("!i", code)
        self.socket.send(msg)


    def brecv_message_control(self):
        data = self.socket.recv(4)
        data = struct.unpack("!i", data)
        return data



    def bsend(self, msg):
        msg = self._bacula_encode(msg)
        bytes = self.socket.send(msg[:4])
        bytes += self.socket.send(msg[4:])

        if DEBUG:
            print msg[4:]
        return bytes


    def brecv(self):

        rdata = []

        while True:

            datasize = self._bacula_decode( self.socket.recv(4) )

            if datasize >= 0:
                data = self.socket.recv(datasize)

                rdata.append(data)
            else:
                break

            if not self.authenticated:
                break

        if DEBUG:
            print "".join(rdata)

        return "".join(rdata)


    def send_and_receive(self, command):
        self.bsend(command)
        return self.brecv()


    def authenticate(self, password, hello_msg='Hello *UserAgent* calling'):
        password = md5.md5(password).hexdigest()

        response = self.send_and_receive(hello_msg)
        challenge = response.split()[2]

        self._auth_response_challenge(challenge, password)
        self._auth_send_challenge(password)
        self.authenticated = True


    authenticate_console = authenticate


    def authenticate_storage(self, password, name):
        hello_msg = 'Hello Director %s calling' % name
        self.authenticate(password, hello_msg)


    authenticate_client = authenticate_storage


    def _auth_response_challenge(self, challenge, password):

        challenge_response = self._get_challenge_response(password, challenge)
        response = self.send_and_receive(challenge_response)


    def _get_challenge_response(self, password, challenge):
        hmac_ = hmac.new(key=password, msg=challenge)
        challenge_response = base64.encodestring(hmac_.digest())
        return challenge_response[:-3]


    def _auth_send_challenge(self, password):
        challenge= _generate_challenge()
        auth_msg = 'auth cram-md5 %s ssl=0\n' % challenge
        response = self.send_and_receive(auth_msg)
        #if response == self._get_challenge_response2( password, challenge):
        # FIX: TODO: (2phase) auth fail. base64 does not match
        msg = '1000 OK auth\n'
        #else:
        #    msg = '1999 Authorization failed.'
        self.send_and_receive(msg)



def _bsocket_maker(port):

    def maker(address):
        bsocket = BSocket()
        bsocket.connect(address, port)
        return bsocket

    return maker


bsocket_storage = _bsocket_maker(9103)
bsocket_client = _bsocket_maker(9102)
bsocket_director = _bsocket_maker(9101)


def _check_status_ok(msg):
    code = int( msg.split()[0] )
    if code % 1000 == 0:
        return True
    return False



def check_storage_service(address, director_name, password):
    bsocket = bsocket_storage(address)
    bsocket.authenticate_storage(password, director_name)
    response = bsocket.send_and_receive('.status current')
    bsocket.close()
    return _check_status_ok(response)


def check_client_service(address, director_name, password):
    bsocket = bsocket_client(address)
    bsocket.authenticate_client(password, director_name)
    response = bsocket.send_and_receive('.status current')
    bsocket.close()
    return _check_status_ok(response)


def check_director_service(address, password):
    bsocket = bsocket_director(address)
    bsocket.authenticate(password)
    response = bsocket.send_and_receive('.status dir current')
    bsocket.close()
    return _check_status_ok(response)



