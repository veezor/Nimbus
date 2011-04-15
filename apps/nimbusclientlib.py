#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import codecs
import socket
import urllib
import urllib2
import cookielib
import subprocess
import simplejson
import securexmlrpc
from glob import glob
from time import sleep
from functools import wraps


#socket.setdefaulttimeout(10)


PLATFORM_MAP = {
    'linux' : 'linux2',
    'windows' : 'win32'
}


CLIENT_CONF = {
    "linux2" : {
        'keypar' : '/etc/nimbus/client.pem',
        'masterkey' : '/etc/nimbus/master.key',
        'fdconf' : '/etc/bacula/bacula-fd.conf',
        'baculafd' : '/etc/init.d/bacula-ctl-fd',
        'xmlrpc_key' : '/etc/nimbus/xmlrpc.key',
        'xmlrpc_cert' : '/etc/nimbus/xmlrpc.cert',
        'auth_token_file' : '/etc/nimbus/auth_token',
    },
    "win32" : {
        'keypar' : 'C:\\Program Files\\Bacula\\client.pem',
        'masterkey' : 'C:\\Program Files\\Bacula\\master.cert',
        'fdconf' : 'C:\\Program Files\\Bacula\\bacula-fd.conf',
        'xmlrpc_key' : 'C:\\Nimbus\\xmlprc.key',
        'xmlrpc_cert' : 'C:\\Nimbus\\xmlprc.cert',
        'auth_token_file' : 'C:\\Nimbus\\auth_token.txt',
    }
}


SSL_CONFIG = dict(C='BR',
                  ST='Rio Grande Do Norte',
                  L='Natal',
                  O='Veezor',
                  OU='Veezor',
                  CN='Veezor')


class PlatformSpecificMethodNotFound(Exception):
    pass


class UnknowPlatform(Exception):
    pass


class PlatformSpecificMethod(object): 

    def __init__(self):
        self.methods = {}


    def on(self, platform):

        def wrapper(method):
            self.register(method, platform)
            return self

        return wrapper

    def register(self, method, platform):
        try:
            platform = PLATFORM_MAP[platform]
        except KeyError, error:
            raise UnknowPlatform(platform)

        self.methods[platform] = method


    def __get__(self, obj, obj_type=None):


        def call(*args, **kwargs):
            try:
                return self.methods[sys.platform](obj, *args, **kwargs)
            except KeyError:
                raise PlatformSpecificMethodNotFound()

        return call




def platform_specific(platform):

    def register(method):
        platform_specific_method = PlatformSpecificMethod()
        platform_specific_method.register(method, platform)
        return platform_specific_method

    return register




def test_platform_specific_method():

    class Test(object):


        @platform_specific('linux')
        def run(self):
            print 'a',self

        @run.on('windows')
        def run(self):
            print 'b'
    


    Test().run()



def is_dir(name):
    if os.path.isdir(name):
        return name + "/"
    return name





def check_auth_token(method):
    
    
    @wraps(method)
    def wrapper(self, token, *args, **kwargs):
        if self._check_auth_token(token):
            return method(self, *args, **kwargs)
        else:
            return 'Answer to the Ultimate Question of Life, the Universe, and Everything=(42)'


    return wrapper


def write_file(filename, content): #python 2.4 support
    f = file(filename, "w")
    try:
        f.write(content)
    finally:
        f.close()


def read_file(filename): #python 2.4 support
    f = file(filename)
    try:
        return f.read()
    finally:
        f.close()


class NimbusService(object):


    def __init__(self):
        self.client_config = self._get_config()


    @check_auth_token
    def save_keys(self, keypar, masterkey):
        try:
            write_file(self.client_config['keypar'], keypar)
            write_file(self.client_config['masterkey'], masterkey)
        except IOError, error:
            return False

        return True


    @check_auth_token
    def save_config(self, config):
        client_config = self._get_config()
        try:
            f = codecs.open(self.client_config['fdconf'], "w", "utf-8")
            try:
                f.write(config)
            finally:
                f.close()
        except IOError, error:
            return False

        return True


    @platform_specific('linux')
    @check_auth_token
    def restart_bacula(self):
        cmd = subprocess.Popen( [self.client_config['baculafd'], "restart"],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE )
        cmd.communicate()
        return True


    @restart_bacula.on('windows')
    @check_auth_token
    def restart_bacula(self):
        cmd = subprocess.Popen(["sc","stop","Bacula-FD"],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE )
        cmd.communicate()
        sleep(3)
        cmd = subprocess.Popen(["sc","start","Bacula-FD"],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE )
        cmd.communicate()
        return True


    @platform_specific('windows')
    @check_auth_token
    def get_available_drives(self):
        import win32api # too ugly :)
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        return drives


    @check_auth_token
    def list_dir(self, path):
        try:
            files = glob(os.path.join(path,'*'))
            files = map(is_dir, files)
            return files
        except IOError, error:
            return []


    def _get_config(self):
        return CLIENT_CONF[sys.platform]


    def _check_auth_token(self, token):
        filename = self.client_config['auth_token_file']
        if os.path.exists(filename):
            auth_token = read_file(filename).strip()
            if token == auth_token:
                return True

        return False

    def hello(self):
        return "Hello world!"




class Notifier(object):
    ADD_COMPUTER_URL = "http://%s:%d/computers/new/"
    LOGIN_URL = "http://%s:%d/session/login/"

    def __init__(self, username, password, address, port=80):
        self.username = username
        self.password = password
        self.ip = address
        self.port = int(port)
        self.cookie = cookielib.CookieJar()
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cookie)
        self.urlopener = urllib2.build_opener(self.cookie_processor)


    def get_url(self, baseurl):
        return baseurl % ( self.ip, self.port )


    def get_computer_data(self):
        args = { "os" :  self.get_os() }
        return urllib.urlencode( args.items() )


    @property
    def csrftoken(self):
        handle = self.urlopener.open( self.get_url(self.LOGIN_URL) )
        content = handle.read()
        handle.close()

        for data in self.cookie:
            if data.name == "csrftoken":
                return data.value


    def get_login_data(self):
        args = { "csrfmiddlewaretoken" :  self.csrftoken,
                 "username" : self.username,
                 "password" : self.password }
        return urllib.urlencode( args.items() )



    def get_os(self):
        if sys.platform in "win32":
            return "windows"
        else:
            return "unix"


    def login(self):
        handle = self.urlopener.open( self.get_url(self.LOGIN_URL),
                                      self.get_login_data() )
        data = handle.read()
        handle.close()


    def notify_new_computer(self):
        self.login()
        handle = self.urlopener.open( self.get_url(self.ADD_COMPUTER_URL),
                                      self.get_computer_data() )
        data = handle.read()
        handle.close()

        token = simplejson.loads(data)['token']
        self.save_auth_token(token)



    def save_auth_token(self, token):
        token = token.strip()
        filename = CLIENT_CONF[sys.platform]['auth_token_file']
        write_file(filename, token)



def get_nimbus_xml_rpc_server():
    key_filename = CLIENT_CONF[sys.platform]['xmlrpc_key']
    cert_filename = CLIENT_CONF[sys.platform]['xmlrpc_cert']
    
    server = securexmlrpc.secure_xmlrpc(key_filename, cert_filename,
                                        ('0.0.0.0',11110),
                                        SSL_CONFIG)

    server.register_instance(NimbusService())
    return server
