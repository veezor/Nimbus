#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
VERSION = "2.3"

import S3
from SOAPpy import SOAPServer
from M2Crypto import SSL
import sys
import MySQLdb
import ConfigParser
import time


try:
	t = open('/etc/nimbus/nimbus_aws_gw.conf')
	t.close()
except: 
	print "File /etc/nimbus/nimbus_aws_gw.conf not found !"
	sys.exit(1)

config = ConfigParser.ConfigParser()
config.read("/etc/nimbus/nimbus_aws_gw.conf")

AWS_ACCESS_KEY_ID = config.get("AWS","aws_access_key_id")
AWS_SECRET_ACCESS_KEY = config.get("AWS","aws_secret_access_key")
HOST = config.get("DB","host")
USER = config.get("DB","username")
PASSWD = config.get("DB","password")
DB = config.get("DB","database")
CERT = config.get("CERT","sslcert")
IP = config.get("NETWORK","address")
PORT = config.get("NETWORK","port")

def generatePUT(key, usuario, senha, md5=""):
	try:
        	conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
        	print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
	cursor = conn.cursor ()
	cursor.execute("SELECT login, senha, bucketname FROM usuarios WHERE login='%s' and senha='%s'" % (usuario,senha))
	row = cursor.fetchone ()
	
	key = "%s/%s" % (usuario,key)

	if row == None:
		cursor.close ()
		conn.close()
		return "NOAUTH","NOID"
	else:
		bucket = row[2]
		generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
		DATETIME = time.ctime()
		cursor.execute("INSERT INTO logging(date,usuario,operation,path) VALUES('%s','%s','PUT','%s')" % (DATETIME, usuario, key))
		cursor.execute("SELECT id FROM logging WHERE date='%s' and usuario='%s' and operation='PUT' and path='%s'" % (DATETIME, usuario, key)) 
		row = cursor.fetchone ()

		if row == None:
			cursor.close ()
			conn.close()
			return "AUTH","NULL"
		else:
			idput = row[0]

			cursor.close ()
			conn.close()
			print "%s - ID %s - URL PUT gerada para o bucket: %s arquivo: %s para o usuário: %s" % (DATETIME,idput,bucket,key,usuario)
			return generator.generate_url('PUT',bucket,key,headers={'Content-MD5': md5}),idput

def generateGET(key, usuario, senha):
	try:
        	conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
        	print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
	cursor = conn.cursor ()
	cursor.execute("SELECT login, senha, bucketname FROM usuarios WHERE login='"+usuario+"' and senha='"+senha+"'")
	row = cursor.fetchone ()

	key = "%s/%s" % (usuario,key)

	if row == None:
		return "NOAUTH","NOID"
	else:
		bucket = row[2]
		generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
		DATETIME = time.ctime()
		cursor.execute("INSERT INTO logging(date,usuario,operation,path) VALUES('%s','%s','GET','%s')" % (time.ctime(), usuario, key))
		cursor.execute("SELECT id FROM logging WHERE date='%s' and usuario='%s' and operation='GET' and path='%s'" % (DATETIME, usuario, key)) 
		row = cursor.fetchone ()

		if row == None:
			return "AUTH","NULL"
		else:
			idget = row[0]
			cursor.close ()
			conn.close()
			print "%s - ID %s - URL GET gerada para o bucket: %s arquivo: %s para o usuário: %s" % (DATETIME,idget,bucket,key,usuario)
			return generator.generate_url('GET',bucket,key),idget

def generateDEL(key, usuario, senha):
	try:
        	conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
        	print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
	cursor = conn.cursor ()
	cursor.execute("SELECT login, senha, bucketname FROM usuarios WHERE login='"+usuario+"' and senha='"+senha+"'")
	row = cursor.fetchone ()
	bucket = row[2]

	key = "%s/%s" % (usuario,key)

	if row == None:
		return "NOAUTH"
	else:
		generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
		cursor.execute("INSERT INTO logging(date,usuario,operation,path) VALUES('%s','%s','DEL','%s')" % (time.ctime(), usuario, key))
		print "%s - URL DEL gerada para o bucket: %s arquivo: %s para o usuário: %s" % (time.ctime(),bucket,key,usuario)
		cursor.close ()
		conn.close()
		return generator.generate_url('DELETE',bucket,key)

def generateLST(usuario, senha,marker):
	try:
        	conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
        	print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
	cursor = conn.cursor ()
	cursor.execute("SELECT login, senha, bucketname FROM usuarios WHERE login='"+usuario+"' and senha='"+senha+"'")
	row = cursor.fetchone ()
	bucket = row[2]

	if row == None:
		return "NOAUTH"
	else:
		generator = S3.QueryStringAuthGenerator(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
		cursor.execute("INSERT INTO logging(date,usuario,operation,path) VALUES('%s','%s','LST','ALL')" % (time.ctime(), usuario))
		print "%s - URL LST gerada para o bucket: %s para o usuário: %s" % (time.ctime(),bucket,usuario)
		cursor.close ()
		conn.close()
		return generator.list_bucket(bucket,options={'marker':marker})
def signalResponse(id, datalen, httpcode):
	try:
		conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit(1)
	cursor = conn.cursor()
	cursor.execute("UPDATE logging SET datalen='%s', httpcode='%s' WHERE id='%s'" % (datalen,httpcode,id))
	DATETIME = time.ctime()
	print "%s - ID %s - Return code %s" % (DATETIME,id,httpcode)
	print "%s - ID %s - Data transfer: %s bytes" % (DATETIME,id,datalen)
	cursor.close()
	conn.close()
	
	
	return "OKUP"

def main():

	
	sslcon = SSL.Context()
	sslcon.load_cert(CERT)

	server = SOAPServer((IP,int(PORT)),ssl_context = sslcon)
	server.registerFunction(generatePUT)
	server.registerFunction(generateGET)
	server.registerFunction(generateDEL)
	server.registerFunction(generateLST)
	server.registerFunction(signalResponse)
	print "Inicializing NimbusGateway version %s by Linconet" % VERSION
	server.serve_forever()

if __name__ == "__main__":
    main()
