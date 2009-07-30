#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from backup_corporativo.bkp.utils import remove_or_leave, absolute_dir_path, absolute_file_path

def sumKey( val, factor ):
    keySum = 0
    if type(val) != type('a2z'):
        val = str(val)
    index = 0
    while index < len(val):
        keySum = factor*keySum + ord(val[index])
        index = index +1
    return keySum

def encrypt(input, output, key, factor, del_original=False):
    factor = int(factor)
    if factor < 0:
        factor = -factor
    factor = (factor % 21) +1
    startPos = sumKey(key, factor)
    fseedpath = absolute_dir_path('custom/fixedseed')
    fcode = open(fseedpath, 'r')
    dummy = fcode.read();
    endPos = fcode.tell()
    while startPos>endPos:
        startPos=startPos-endPos
    fcode.seek( startPos )
    fout = open( output, 'w')
    fin = open(input)
    for line in fin:
        for ch in line:
            val = ord(ch)
            ch1 = fcode.read(1)
            if ch1:
                val = ( val + ord(ch1) ) % 256
                fout.write(chr(val))
                if ch1 == '':
                    fcode.seek( 0 )            
    fin.close()
    fout.close()
    fcode.close()
    if del_original:
        remove_or_leave(input)



def decrypt(input, output, key, factor, del_original=False):
    if factor < 0:
        factor = -factor
    factor     = (factor % 21) +1
    startPos   = sumKey( key, factor )

    fseedpath = absolute_path('custom/fixedseed')
    fcode = open(fseedpath, 'r')

    dummy = fcode.read();
    endPos = fcode.tell()
    while startPos>endPos:
        startPos=startPos-endPos
    fcode.seek( startPos )
    fout = open( output, 'w')
    fin = open(input)
    for line in fin:
        for ch in line:
            val = ord(ch)
            ch2 = fcode.read(1)
            val = ( val - ord(ch2) ) % 256
            fout.write(chr(val))
            if ch2 == '':
                fcode.seek( 0 )      
    fin.close()
    fout.close()
    fcode.close()
    if del_original:
        remove_or_leave(input)

# TODO: Refazer função para gerar master.key        
#def generate_master_kp():
#    key = gen_key('master')
#    cert = gen_cert('master',key)


GENERATE_KEY_RAW_CMD = "openssl genrsa -out %(out)s 2048"
GENERATE_CERT_RAW_CMD = "openssl req -new -key %(key_path)s -x509 -out %(out)s"
GET_PEM_RAW_CMD = "cat %(key_path)s %(cert_path)s"
