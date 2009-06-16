from __future__ import with_statement
import os

def remove_or_leave(filepath):
    "remove file if exists"
    try:
        os.remove(filepath)
    except os.error:
        # Leave
        pass

def absolute_path(rel_dir):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), rel_dir)


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
    fseedpath = absolute_path('custom/fixedseed')
    fcode = open(fseedpath, 'r')
    dummy = fcode.read();
    endPos = fcode.tell()
    while startPos>endPos:
        startPos=startPos-endPos
    fcode.seek( startPos )
    fout = open( output, 'w')
    with open(input) as fin:
        for line in fin:
            for ch in line:
                val = ord(ch)
                ch1 = fcode.read(1)
                if ch1:
                    val = ( val + ord(ch1) ) % 256
                    fout.write(chr(val))
                    if ch1 == '':
                        fcode.seek( 0 )            
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
    with open(input) as fin:
        for line in fin:
            for ch in line:
                val = ord(ch)
                ch2 = fcode.read(1)
                val = ( val - ord(ch2) ) % 256
                fout.write(chr(val))
                if ch2 == '':
                    fcode.seek( 0 )      
    fout.close()
    fcode.close()
    if del_original:
        remove_or_leave(input)
