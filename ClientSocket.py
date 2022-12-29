#----- SOCKET -----
import socket

#----- Parsing ------ 
from urllib.parse import unquote
from urllib.parse import urlparse

#----- mkdir -----
import os

#----- CONSTANTS & GLOBAL Vars -----
DEFAULT_PORT = 80
BUF_SIZE = 4196*4


class ClientSocket:
	def __init__(self) -> None:
		self.s = socket.socket()
		self.HOST = ''

	def __del__(self):
		self.s.close()

	def downloadFileCLength(self, fileName: str, savePath: str = '', contentLength = BUF_SIZE):	#savePath has default empty value (for current directory download)
		#----- WRITE TO FILE ------
		fileName = unquote(fileName) #to decode URL special characters (i.e. %20 means whitespace: ' ')
		print('Downloading',fileName)
		with open(savePath + ('/' if savePath else '') + fileName, "wb") as fileWrite:

			# #Write redundant bytes in last header recv to the file, which are not header but Content
			# fileWrite.write(recvBUF)
			# recvCount = len(recvBUF)
			recvCount = 0
			while (recvCount < contentLength):
				data = self.s.recv(contentLength) # Get response
				
				#Raise error if recv NOTHING
				if len(data) == 0:
					raise RuntimeError("socket connection broken")

				#<socket variable>.recv(number of bytes of data)
				#data is used to store information that is requested above
				fileWrite.write(data)
				recvCount += len(data) 	#increase the count by number of read bytes



	def downloadFileChunked(self, fileName: str, savePath: str):
		with open(savePath + ('/' if savePath else '') + (fileName if fileName else 'index.html'), "wb") as fileWrite:
			data = None
			flag = b''

			while (1):
				bytesToWriteHex = b''

				#Take the length of chunks in hex
				while (flag != b"\n"):
					data = self.s.recv(1)
					flag = data
					if (flag != b"\r"):
						bytesToWriteHex += flag


				#Convert string to int
				if (bytesToWriteHex != b""):
					bytesToWriteInt = int(bytesToWriteHex.decode(), base=16)

				if bytesToWriteInt == 0: break

				#Write data
				recvCount = 0
				while(recvCount < bytesToWriteInt):
					fileWrite.write(self.s.recv(1))
					recvCount += 1
				#To bypass /r/n at the end message
				data = self.s.recv(2)

				flag = ""

	def downloadFile(self, downloadPath: str(), fileName: str, savePath = ""):

		get = "GET " + downloadPath + " HTTP/1.1\r\n"
		connection = 'Connection: keep-alive\r\n'
		keepAlive = "Keep-Alive: timeout=5, max=1000\r\n"
		host = "Host: " + self.HOST + '\r\n'
		request = get + host + connection + keepAlive + "\r\n"

		#----- SEND REQUEST -----
		sent = self.s.send(request.encode()) #Request must be encoded, so we have to use encode() function
		if sent == 0:
			raise RuntimeError("socket connection broken")
		
		#----- GET HEADER ------

		header = b''
		flag = b''
		while (flag != b"\r\n\r\n"):
			data = self.s.recv(1)

			if (flag == b"\r\n\r"):
				if (data == b"\n"):
					flag += data
					header += data
				else:
					header += data
					flag = b''


			elif (flag == b"\r\n"):
				if (data == b"\r"):
					flag += data
					header += data
				else:
					header += data
					flag = b''

			elif (flag == b"\r"):
				if (data == b"\n"):
					flag += data
					header += data
				else:
					header += data
					flag = b''

			elif (data == b"\r"):
					flag += data
					header += data

			else: #normal data: header
				header += data

		#----- ERR HANDLING ------
		if header.find(b'404 Not Found') != -1:
			print('Error 404 Not Found ', fileName )
			return
		if header.find(b'301 Moved Permanently') != -1:
			print('Error 301 Moved Permanently')
			return
		
		# if no err happens, then continue downloading

		#----- DECIDE DOWNLOAD MODE -----
		# if header has 'chunked' then call chunked
		if (header.find(b'chunked') != -1):
			self.downloadFileChunked(fileName, savePath)
		else:
			#Get Content-Length from header
			contentLengthIndex = header.find(b'Content-Length:')
			n = header[contentLengthIndex + 16: header.find(b'\r\n', contentLengthIndex + 16)].decode()
			contentLength = int(n)
			self.downloadFileCLength(fileName, savePath, contentLength)

		


	def downloadFolder(self, url):
		partsList = url.path.rstrip('/').split('/')
		domain = url.hostname

		#----- Create folder: domain_folderName ------
		downloadFolderName = domain + '_' + partsList[-1]
		if not os.path.exists(downloadFolderName):
			os.mkdir(downloadFolderName)


		#----- DOWNLOAD index.html -----
		self.downloadFile(url.path, 'index.html', downloadFolderName)

		#----- Parsing the index.html and looping downloadFile-----
		with open(downloadFolderName + '/index.html', 'r') as fin:
			indexHTML = fin.read()

		URLindex = 0
		while (1):
			URLindex = indexHTML.find('href="', URLindex)
			if (URLindex == -1):
				print('Complete Download the folder',downloadFolderName)
				break
			#Move the index to file start pos (6 is size of 'href="')
			URLindex += 6

			#Extract fileName from index.html
			fileName = indexHTML[URLindex : indexHTML.find('"', URLindex)]

			#if the fileName is not a file name:
			if (fileName.find('.') == -1):
				continue

			#----- DOWNLOAD a FILE from FOLDER -----
			self.downloadFile(url.path + '/' + fileName, fileName, downloadFolderName)





	#----- SOCKET CONNECT -----
def handleConnection(address: str()):
	url = urlparse(address)

	#----- Creating ClientSocket object
	cs = ClientSocket()
	cs.HOST = url.hostname

	# ----- CREATING SOCKET -----
	cs.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#socket.socket(addr_family, type)
	#This is used to create a socket
	#socket.AF_INET is IPv4
	#socket.SOCK_STREAM is TCP

	#----- CONNECT -----
	cs.s.connect((cs.HOST, DEFAULT_PORT)) # Connect
	#<socket variable>.connect(("address", port))

	
	if len(url.path) > 1:
		#if the path contain '.' -> means it's a file, then downloadFile
		if (url.path.find('.') == -1):
			cs.downloadFolder(url)
		else:
			cs.downloadFile(url.path, url.hostname + '_' + url.path.rstrip('/').split('/')[-1])

	else:	#Với các request là "/" gốc thì mặc định tải và lưu thành file '<domain>_index.html'
		cs.downloadFile('/', url.hostname + '_index.html')
