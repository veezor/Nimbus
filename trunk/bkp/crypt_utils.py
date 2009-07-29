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
        
def generate_master_kp():
    key = gen_key('master')
    cert = gen_cert('master',key)

def generate_fd_kp(client_name):
    key = gen_key(client_name)
    cert = gen_cert(client_name,key)
    pem = gen_pem(client_name,key,cert)


def gen_key(client_name):
    TMP_KEYS_REL_PATH = "custom/tmp/keys/"
    fname = "fd-%(client_name)s.key" % {'client_name':client_name}
    key_path = absolute_file_path(fname,TMP_KEYS_REL_PATH)
    cmd = "openssl genrsa -out %(out)s 2048" % {'out':key_path}
    try:
        os.system(cmd)
        return key_path
    except: #TODO: Catch only IOError
        return ''

def gen_cert(client_name, key_path):
    TMP_CERTS_REL_PATH = "custom/tmp/certs/"
    fname = "fd-%(client_name)s.cert" % {'client_name':client_name}
    cert_path = absolute_file_path(fname,TMP_CERTS_REL_PATH)
    cmd = "openssl req -new -key %(fdkey)s -x509 -out %(out)s" % {'fdkey':key_path, 'out':cert_path}
    try:
        os.system(cmd)
        return cert_path
    except: #TODO: Catch only IOError
        return ''

       
def gen_pem(client_name,key_path, cert_path):
    TMP_PEMS_REL_PATH = "custom/tmp/keys/"
    fname = "fd-%(client_name)s.key" % {'client_name':client_name}
    pem_path = absolute_file_path(fname,TMP_PEMS_REL_PATH)
    cmd = "cat %(fdkey)s %(fdcert)s > %(out)s" % {'fdkey':key_path,'fdcert':cert_path,'out':pem_path}
    try:
        os.system(cmd)
        return pem_path
    except: #TODO Catch only specific error
        return ''
    