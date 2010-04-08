#!/usr/bin/env python
# -*- coding: UTF-8 -*-



import base64
import simplejson
import urllib
import urllib2
import urlparse
import pycurl
import md5
import os



class _File(object):

    def __init__(self, filename, mode, callback):
        self.fileobj = file(filename, mode)
        self.callback = callback
        self.filesize = os.path.getsize(filename)
        self.bytes_read = 0


    def read(self, size):
        r =  self.fileobj.read(size)
        self.bytes_read += size
        return r

    def progress_download(self, totaldown, downloaded, totalup, uploaded):
        if self.callback:
            self.callback( totaldown, downloaded )


    def progress_upload(self, totaldown, dowloaded, totalup, uploaded):
        if self.callback:
            self.callback( totalup, uploaded )


    def close(self):
        self.fileobj.close()


def _md5_for_file(filename, block_size=2**20):
    fileobj = file(filename, 'rb')
    filemd5 = md5.md5()
    while True:
        data = fileobj.read(block_size)
        if not data:
            break
        filemd5.update(data)
    fileobj.close()
    return filemd5.digest()


class Api(object):


    def __init__(self, username, password, gateway_url, encoding=None):
        self.username = username
        self.password = password
        self.encoding = encoding
        self.url = gateway_url

    def _fetch_url(self, url, **post_data):
        # Get a url opener that can handle basic auth
        opener = self._get_opener(url)

        encoded_post_data = self._encode_post_data(post_data)

        url_data = opener.open(url, encoded_post_data).read()
        opener.close()
        data = simplejson.loads(url_data)
        return data
   
    def _encode_post_data(self, post_data):
        if not post_data:
            return None
        return urllib.urlencode( dict( [ (k, self._encode(v)) for k, v in post_data.items()]))

    def _encode(self, data):
        if self.encoding:
            return unicode(data, self.encoding).encode('utf-8')
        else:
            return unicode(data).encode('utf-8')

    def _get_opener(self, url):
        handler = urllib2.HTTPBasicAuthHandler()
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(url)
        handler.add_password("Restricted Access", netloc, self.username, self.password)
        opener = urllib2.build_opener(handler)
        return opener

    def get_file_url(self, filepath):
        url = self.url + "/json/get"
        return self._fetch_url(url, path=filepath)

    def get_upload_url(self, filepath, base64_of_md5):
        url = self.url + "/json/put"
        return self._fetch_url(url, path=filepath, base64_of_md5=base64_of_md5)

    def get_delete_url(self, filepath):
        url = self.url + "/json/delete"
        return self._fetch_url(url, path=filepath)

    def get_list_url(self):
        url = self.url + "/json/list"
        return self._fetch_url(url)

    def download_file(self, filename, dest, limitrate=None, callback=None, overwrite=False):
        url = self.get_file_url(filename)['url']

        mode = "wb"
        resume = False

        if os.path.exists(dest) and not overwrite:
            resume = True
            resume_index = os.path.getsize(dest)
            mode = "ab"

        fp = _File(dest, mode, callback)
        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)
        curl.setopt(pycurl.NOPROGRESS, 1)

        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.WRITEDATA, fp.fileobj)

        if resume:
            curl.setopt(pycurl.RESUME_FROM_LARGE, resume_index)

        if callback:
            curl.setopt( pycurl.PROGRESSFUNCTION, 
                         fp.progress_download)

        if limitrate:
            curl.setopt(pycurl.MAX_RECV_SPEED_LARGE, limitrate)


        curl.perform()
        curl.close()
        fp.close()


    def delete_file(self, filename):

        url = self.get_delete_url(filename)['url']
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.CUSTOMREQUEST, "DELETE")
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.perform()
        curl.close()




    def upload_file(self, filename, dest, limitrate=None, callback=None):

        filemd5 = _md5_for_file(filename)
        base64_of_md5 = base64.standard_b64encode(filemd5)
        filereader = _File(filename, "rb", callback)

        url = self.get_upload_url(dest, base64_of_md5)['url']

        curl = pycurl.Curl()

        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.UPLOAD, 1)
        curl.setopt( pycurl.READFUNCTION, 
                     filereader.read )

        curl.setopt(pycurl.INFILESIZE, filereader.filesize)
        curl.setopt(pycurl.NOPROGRESS, 1)
        curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        curl.setopt(pycurl.TIMEOUT, 300)
        curl.setopt(pycurl.HTTPHEADER, ["Content-MD5:" + base64_of_md5])
        curl.setopt(pycurl.NOSIGNAL, 1)

        if callback:
            curl.setopt( pycurl.PROGRESSFUNCTION, 
                         filereader.progress_upload)

        if limitrate:
            curl.setopt(pycurl.MAX_SEND_SPEED_LARGE, limitrate)

        curl.perform()
        curl.close()



 
