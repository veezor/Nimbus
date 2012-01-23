#!/usr/bin/python
# -*- coding: utf-8 -*-


from hashlib import md5



class Md5CheckError(Exception):
    pass


def md5_for_large_file(filename, block_size=2**20):
    fileobj = file(filename, 'rb')
    filemd5 = md5()
    while True:
        data = fileobj.read(block_size)
        if not data:
            break
        filemd5.update(data)
    fileobj.close()
    return filemd5.hexdigest()


