#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import boto
from boto.s3 import connection as boto_s3_connection_class
from boto.s3.key import Key
import logging
import tempfile
from functools import wraps
from time import sleep, time
from cStringIO import StringIO
from boto.s3.resumable_download_handler import ResumableDownloadHandler

#from nimbus.offsite import queue_service
#from nimbus.offsite.models import Offsite

MIN_MULTIPART_SIZE = 5242880 # 5mb

logging.getLogger('boto').setLevel(logging.CRITICAL)




class RateLimiter(object):
    """Rate limit a url fetch"""


    def __init__(self, rate_limit):
        """rate limit in kBytes / second"""
        self.rate_limit = rate_limit
        self.start = time()


    def __call__(self, transferred_size, total_size):

        total_kb = float(total_size) / 1024
        transferred_size = float(transferred_size) / 1024 #kb
        elapsed_time = time() - self.start

        if elapsed_time:

            rate = transferred_size / elapsed_time


            expected_time = transferred_size / self.rate_limit

            sleep_time = expected_time - elapsed_time

            if sleep_time > 0:
                sleep(sleep_time)



class MultipartFileManager(object):

    MB_SIZE = MIN_MULTIPART_SIZE

    def __init__(self, filename, part=0):
        self.next_part_number = part
        self.filename = filename
        self.file = file(self.filename)
        self.finish = False

    def __enter__(self):
        self.file.__enter__()
        return self

    def __exit__(self, *excinfo):
        self.file.__exit__(*excinfo)

    def __iter__(self):
        return self

    def next(self):

        if self.next_part_number == -1:
            raise StopIteration()

        self.file.seek( self.MB_SIZE * self.next_part_number)
        data = self.file.read( self.MB_SIZE )

        if len(data) != self.MB_SIZE:
            self.finish = True
            self.next_part_number = -1
            raise StopIteration()
        else:
            self.next_part_number += 1

        return data


    

class S3AuthError(Exception):
    pass



def multipart_status_callback_template(filename, part):
    pass


def report_status_callback_template(transferred_size, total_size):
    pass


class CallbackAggregator(object):

    def __init__(self, *callbacks):
        self.callbacks = list(callbacks)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        self.callbacks.remove(callback)

    def __call__(self, *args, **kwargs):
        for callbacks in self.callbacks:
            callbacks(*args, **kwargs)



def callback_decorator(function):
    "Add callback parameter to S3 methods"
    
    @wraps(function)
    def wrapper(self, *args, **kwargs):

        callback = kwargs.pop('callback', None)

        if callback:
            self.callbacks.add_callback(callback)

        value = function(self, *args, **kwargs)

        if callback:
            self.callbacks.remove_callback(callback)
        
        return value

    return wrapper


class S3(object):


    def __init__(self, username, access_key, secret_key,
                       rate_limit=None, host=None):

        self.username = username
        self.access_key = access_key
        self.secret_key = secret_key
        self.rate_limit = rate_limit
        self.rate_limiter = RateLimiter(self.rate_limit)
        self.callbacks = CallbackAggregator()
        self.multipart_status_callbacks = CallbackAggregator()
        self.host = host
        self.logger = logging.getLogger(__name__)

        if self.rate_limit:
            self.callbacks.add_callback(self.rate_limiter)

        if self.host =='s3.amazonaws.com':
            self.connection = boto.connect_s3(self.access_key, self.secret_key)
        else:
            self.connection = boto.connect_s3(aws_access_key_id=self.access_key,
                              aws_secret_access_key=self.secret_key,
                              is_secure=False,
                              host=self.host,
                              port=8773,
                              calling_format=boto_s3_connection_class.OrdinaryCallingFormat(),
                              path="/services/Walrus")

        if not self.connection:
            raise S3AuthError("check access_key and secret_key")

        self.bucket = self.connection.lookup(username)
        if not self.bucket:
            raise S3AuthError("check access_key and secret_key")


    def list_files(self):
        return [ item for item in self.bucket.list() if isinstance(item, Key)]


    def _upload(self, filename, keyname):
        self.logger.info('simple upload')
        key = self.bucket.new_key(keyname)
        with file(filename) as f_obj:
            key.set_contents_from_file(f_obj,
                                       cb=self.callbacks,
                                       num_cb=-1)


    def _upload_multipart(self, filename, keyname, part):
        from nimbus.offsite import queue_service

        self.logger.info('initiate multipart upload ')
        multipart = self.bucket.initiate_multipart_upload(keyname)

        self.logger.info('initiate multipart with part =  %d' % (part)  )


        with MultipartFileManager(filename, part) as manager:
            for (part_number, part_content) in enumerate(manager, part):

                self.rate_limiter.rate_limit = queue_service.get_worker_ratelimit()

                part_file = StringIO(part_content)
                multipart.upload_part_from_file(part_file,
                                                part_number + 1,
                                                cb=self.callbacks,
                                                num_cb=-1)

                self.multipart_status_callbacks(filename, part_number)

        multipart.complete_upload()


    def cancel_multipart_upload(self, filename):
        for part in self.bucket.list_multipart_uploads():
            if part.key_name == filename:
                self.bucket.cancel_multipart_upload( part.key_name, part.id)


    @callback_decorator
    def upload_file(self, filename, key=None, part=0):
        self.logger.info('initiate upload with part =  %d' % (part)  )

        if not key:
            key = os.path.basename(filename)

        size = os.path.getsize(filename)

        if size < MIN_MULTIPART_SIZE:
            self._upload(filename, key)
        else:
            self._upload_multipart(filename, key, part)



    @callback_decorator
    def download_file(self, filename, destination=None):

        if not destination:
            destination = filename

        key = self.bucket.get_key(filename)
        handler = ResumableDownloadHandler(tempfile.mktemp())
        handler._save_tracker_info(key) # Ugly but necessary
        with file(destination, "a") as f:
            handler.get_file(key, f, {}, cb=self.callbacks, num_cb=-1)



    def delete_file(self, filename):
        self.bucket.delete_key(filename)


    def get_size(self):
        entries = self.list_files()
        return sum( key.size for key in entries )


    def get_plan_size(self):
        from nimbus.offsite.models import Offsite
        conf = Offsite.get_instance()
        return conf.plan_size


    def get_usage(self):
        return float(self.get_size())/self.get_plan_size()
  
