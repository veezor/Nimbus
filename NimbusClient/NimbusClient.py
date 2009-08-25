#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
VERSION="0.1"

import os
import sys
from SOAPpy import SOAPProxy
import md5
import MySQLdb
import ConfigParser
import time
import pilha
import base64


def dbConnect(HOST,USER,PASSWD,DB):
	try:
		conn=MySQLdb.connect (host=HOST,user=USER,passwd=PASSWD,db=DB)
	except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit (1)
	return conn


def generateStack(volumes,PATH,DBCONN):
	
	cursor = DBCONN.cursor()
	cursor.execute("UPDATE arquivos SET stacked='no'")
	stack = pilha.Stack()
	for volume in volumes :
		ctime=time.ctime(os.path.getmtime(PATH+volume))
		cursor.execute("SELECT data FROM arquivos WHERE nomearquivo='"+volume+"'")
		row = cursor.fetchone ()
		if row == None: 
			cursor.execute ("INSERT INTO arquivos(nomearquivo,data,status) VALUES('"+volume+"','"+ctime+"','toup')")
			stack.push(volume)
			cursor.execute("UPDATE arquivos SET stacked='yes' WHERE nomearquivo='"+volume+"'")
		else:
			if row[0] != ctime:
				cursor.execute("UPDATE arquivos SET data='"+ctime+"', status='toup' WHERE nomearquivo='"+volume+"'")
				stack.push(volume)
				cursor.execute("UPDATE arquivos SET stacked='yes' WHERE nomearquivo='"+volume+"'")

	if stack.isEmpty():
		return "Empty Stack"
	
	
	cursor.close ()
	DBCONN.close()
	return stack

def SOAPConnect(IPSERVER, PORT):
	server = SOAPProxy("https://"+IPSERVER+":"+PORT)
	return server


def uploadVolumes(DBCONN,STACK,PATH,SOAPSERVER,NLOGIN,NPASSWD,NSPEED) :
	os.chdir(PATH)
	cursor = DBCONN.cursor()
	if STACK.isEmpty():
		return "Empty Stack"
	volume = STACK.pop()

	FILEMD5 = file(volume,'rb')
	MD5 = md5.new(FILEMD5.read()).digest()
	MD5BASE64 = base64.standard_b64encode(MD5)
	FILEMD5.close()

	url,idput = SOAPSERVER.generatePUT(volume,NLOGIN,NPASSWD,MD5BASE64)

	if url == "NOAUTH":
		print "User or Password invalid!"
		##raise SystemExit
		#break
		return "NOAUTH"
	
	os.system("curl -H Content-MD5:"+MD5BASE64+" \""+url+"\" -T "+volume+" -f --limit-rate "+str(NSPEED)+"K -s -w \"%{http_code}\" > /etc/nimbus/httpcodeout")
	httpcode = open('/etc/nimbus/httpcodeout','r')
	CODE = httpcode.read()
	ARQ = file(volume,'rb')
	ARQ.seek(0,2)
	DATALEN = ARQ.tell()
	signal = SOAPSERVER.signalResponse(idput,DATALEN,CODE)
	if CODE != "200":
		print "HTTP Error: "+CODE
		##raise SystemExit
		#break
		return "HTTP Error"
   
	cursor.execute("UPDATE arquivos SET status='up' WHERE nomearquivo='"+volume+"'")
	cursor.close()
	DBCONN.close()
	print "Volume "+volume+" enviado ao Amazon S3 e atualizado no banco de dados"
	
	return "OKUP"

def main():
	try:
	    t = open('/etc/nimbus/nimbus_client.conf')
	    t.close()
	except:
	    print "File /etc/nimbus/nimbus_client.conf not found !"
	    sys.exit(1)

	configclient = ConfigParser.ConfigParser()
	configclient.read("/etc/nimbus/nimbus_client.conf")

	HOST = configclient.get("DB","host")
	USER = configclient.get("DB","username")
	PASSWD = configclient.get("DB","password")
	DB = configclient.get("DB","database")
	PATH = configclient.get("PATH","backup")
	IPSERVER = configclient.get("NETWORK","server")
	PORT = configclient.get("NETWORK","port")
	NLOGIN = configclient.get("NIMBUS","login")
	NPASS = configclient.get("NIMBUS","password")
	NSPEED = configclient.get("NIMBUS","speed")

	VOLUMES = sys.argv[1].split("|")
	print VOLUMES
	
	dbconn = dbConnect(HOST,USER,PASSWD,DB)
	stack = generateStack(VOLUMES,PATH,dbconn)
	soapserver = SOAPConnect(IPSERVER, PORT)

	passwd = md5.new(NPASS).hexdigest()

	FDBK = "CONTINUE"
	RETRYCOUNT = 0
	while (FDBK == "CONTINUE" and RETRYCOUNT < 3):

		dbconn = dbConnect(HOST,USER,PASSWD,DB)
		rtncd = uploadVolumes(dbconn,stack,PATH,soapserver,NLOGIN,passwd,NSPEED)
		if rtncd == "Empty Stack":
			FDBK = "STOP"
		if rtncd == "HTTP Error" or rtncd == "NOAUTH":
			print "Retrying..."			
			RETRYCOUNT = RETRYCOUNT + 1	
			time.sleep(60)
			stack = generateStack(PATH,dbconn)

if __name__ == "__main__":
	main()
