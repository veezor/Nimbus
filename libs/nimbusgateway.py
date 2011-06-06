#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import base64
import simplejson
import urllib
import urllib2
import urlparse
import pycurl
import hashlib
import os
import S3

class _S3HttpResponseFake(object):

    def __init__(self, content):
        self.status = 200
        self.reason = "OK"
        self.content = content

    def read(self):
        return self.content

class File(object):

    def __init__(self, filename, mode, callback):
        self.fileobj = file(filename, mode)
        self.callback = callback
        self.filesize = os.path.getsize(filename)
        self.read_bytes = 0
        self.written_bytes = 0


    def read(self, size):
        r =  self.fileobj.read(size)
        self.read_bytes += size
        self.progress_upload( )
        return r

    def write(self, content):
        size = len(content)
        r = self.fileobj.write(content)
        self.written_bytes += size
        self.progress_download( )
        return r

    def progress_download(self):
        if self.callback:
            self.callback( self.written_bytes, self.filesize )


    def progress_upload(self):
        if self.callback:
            self.callback( self.read_bytes, self.filesize )


    def header_callback(self, line):
        if line.startswith("Content-Length:"):
            header, size = line.split()
            self.filesize = int(size)

    def close(self):
        self.fileobj.close()


def _md5_for_file(filename, block_size=2**20):
    fileobj = file(filename, 'rb')
    filemd5 = hashlib.md5()
    while True:
        data = fileobj.read(block_size)
        if not data:
            break
        filemd5.update(data)
    fileobj.close()
    return filemd5.digest()


class Api(object):

    MAX_RETRY = 3


    def __init__(self, username, password, gateway_url, encoding=None):
        self.username = username
        self.password = password
        self.encoding = encoding
        self.url = gateway_url


    def _fetch_json_url(self, url, **post_data):
        url_data = self._fetch_url(url, **post_data)
        data = simplejson.loads(url_data)
        return data


    def _fetch_url(self, url, **post_data):

        opener = self._get_opener(url)
        encoded_post_data = self._encode_post_data(post_data)
        url_data = opener.open(url, encoded_post_data).read()
        opener.close()

        return url_data


   
    def _encode_post_data(self, post_data):
        if not post_data:
            return None
        return urllib.urlencode( dict( [ (k, self._encode(v)) \
                                    for k, v in post_data.items()]))

    def _encode(self, data):
        if self.encoding:
            return unicode(data, self.encoding).encode('utf-8')
        else:
            return unicode(data).encode('utf-8')

    def _get_opener(self, url):
        handler = urllib2.HTTPBasicAuthHandler()
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)

        handler.add_password( "Restricted Access", 
                              netloc,  self.username, self.password)

        opener = urllib2.build_opener(handler)
        return opener


    def check_auth(self):
        return self._fetch_url(self.url + "/check_auth")


    def get_file_url(self, filepath):
        url = self.url + "/json/get"
        return self._fetch_json_url(url, path=filepath)

    def get_upload_url(self, filepath, base64_of_md5):
        url = self.url + "/json/put"
        return self._fetch_json_url(url, path=filepath, 
                                    base64_of_md5=base64_of_md5)

    def get_delete_url(self, filepath):
        url = self.url + "/json/delete"
        return self._fetch_json_url(url, path=filepath)

    def get_list_url(self, marker=None):

        options = {}

        if marker:
            options["marker"] = marker

        url = self.url + "/json/list"
        return self._fetch_json_url(url, **options)

    def download_file( self, filename, dest, 
                       ratelimit=None, callback=None, overwrite=False):

        url = self.get_file_url(filename)['url']
        self._download_file( url, dest, ratelimit, callback, overwrite ) 


    def _download_file( self, url, dest, 
                       ratelimit=None, callback=None, overwrite=False):
        mode = "wb"
        resume = False

        if os.path.exists(dest) and not overwrite:
            resume = True
            resume_index = os.path.getsize(dest)
            mode = "ab"

        fileobj = File(dest, mode, callback)
        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, str(url))
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)
        curl.setopt(pycurl.NOPROGRESS, 1)

        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.WRITEFUNCTION, fileobj.write)
        curl.setopt(pycurl.HEADERFUNCTION, fileobj.header_callback)

        if resume:
            curl.setopt(pycurl.RESUME_FROM_LARGE, resume_index)


        if ratelimit and ratelimit != -1:
            curl.setopt(pycurl.MAX_RECV_SPEED_LARGE, ratelimit)

        try:
            curl.perform()
        except pycurl.error, e:
            code, msg = e
            if code == 18:#transfer closed with outstanding read data remaining
                pass
            else:
                raise 

        curl.close()
        fileobj.close()


    def delete_file(self, filename):

        url = self.get_delete_url(filename)['url']
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, str(url))
        curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.perform()
        curl.close()




    def upload_file(self, filename, dest, sent_md5=True,
                    ratelimit=None, callback=None):

        if sent_md5:
            filemd5 = _md5_for_file(filename)
            base64_of_md5 = base64.standard_b64encode(filemd5)

        filereader = File(filename, "rb", callback)

        url = self.get_upload_url(dest, base64_of_md5)['url']

        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, str(url))
        curl.setopt(pycurl.UPLOAD, 1)
        curl.setopt( pycurl.READFUNCTION, 
                     filereader.read )

        curl.setopt(pycurl.INFILESIZE, filereader.filesize)
        curl.setopt(pycurl.NOPROGRESS, 1)
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)

        if sent_md5:
            curl.setopt(pycurl.HTTPHEADER, ["Content-MD5:" + base64_of_md5])

        curl.setopt(pycurl.NOSIGNAL, 1)

        if ratelimit:
            curl.setopt(pycurl.MAX_SEND_SPEED_LARGE, ratelimit)

        curl.perform()
        curl.close()


    def list_files(self, marker=None):
        info = self.get_list_url(marker)
        content = self._fetch_url(info['url'])
        if info['service'] == 'amazon':
            items = S3.ListBucketResponse( _S3HttpResponseFake(content))
            truncated = items.is_truncated
            return [ (e.key, e.size) for e in items.entries ], truncated


    def list_all_files(self):
        result = []
        entries, is_truncated = self.list_files()
        result.extend( entries )

        while is_truncated:

            retry = 0
            
            while retry < self.MAX_RETRY:
                try:
                    last = result[-1][0] # entries = [ (file, size) ]
                    entries, is_truncated = self.list_files(marker=last)
                    result.extend( entries )
                    break
                except urllib2.URLError, e:
                    retry += 1

        return result
        


    def get_size(self):
        entries = self.list_all_files()
        return sum( e[1] for e in entries )


    def get_plan_size(self):
        url = self.url + "/json/plan_size"
        return self._fetch_json_url(url)['size']

    def get_usage(self):
        return float(self.get_size())/self.get_plan_size()





 
