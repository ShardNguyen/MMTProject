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

#---- Đưa hết các method liên quan vào 1 class
# Chia sẻ vài attribute chung: socket, HOST
class ClientSocket:
	#----- Constructor -----
	def __init__(self) -> None:
		# ----- CREATING SOCKET -----
		self.s = socket.socket()

		self.HOST = ''	#Chứa tên miền - domain


	#----- Destructor -----
	def __del__(self):
		self.s.close()


	def startConnection(self):
		try:
			self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				#socket.socket(addr_family, type)
				#This is used to create a socket
				#socket.AF_INET is IPv4
				#socket.SOCK_STREAM is TCP

			self.s.settimeout(30) #set time out cho 1 lần recv() là 30 giây
			self.s.connect((self.HOST, DEFAULT_PORT))

			#<socket variable>.connect(("address", port))
		except:
			print("Socket Timeout Err")
			return False
		return True


	#----- Close Connection -----
	def closeConnection(self):
		# SHUTDOWN: đóng connection, nhưng để lại buffer để đọc nốt mấy cái còn dư
		# CLOSE: Huỷ xoá bộ nhớ mà socket đang nắm giữ
		self.s.shutdown(socket.SHUT_RDWR)
		self.s.close()


	def sendRequest(self, downloadPath: str(), attemps: int() = 0) -> bool:
		#If 3 attemmps are made but failed, drop file.
		if (attemps == 3):
			print("Cannot send request, skipping...")
			return False
		
		#Generate Request
		get = "GET " + downloadPath + " HTTP/1.1\r\n"
		connection = 'Connection: keep-alive\r\n'
		keepAlive = "Keep-Alive: timeout=5, max=1000\r\n"
		host = "Host: " + self.HOST + '\r\n'
		request = get + host + connection + keepAlive + "\r\n"


		#----- SEND REQUEST -----
		sent = self.s.send(request.encode()) #Request must be encoded, so we have to use encode() function
		if sent == 0:
			print("Cannot send request, trying to reconnect")
			self.closeConnection()
			self.startConnection()
			self.sendRequest(downloadPath, attemps + 1)
		
		return True


	def downloadFileCLength(self, fileName: str, savePath: str = '', contentLength = BUF_SIZE) -> bool:	#savePath has default empty value (for current directory download)
		#----- WRITE TO FILE ------
		fileName = unquote(fileName) #to decode URL special characters (i.e. %20 means whitespace: ' ')
		print('Downloading',fileName)

		with open(savePath + ('/' if savePath else '') + fileName, "wb") as fileWrite:
			recvCount = 0
			while (recvCount < contentLength):
				data = self.s.recv(contentLength) # Get response
				
				#Raise error if recv NOTHING
				if len(data) == 0:
					print("socket connection broken")
					self.closeConnection()
					return False

				# <socket variable>.recv(number of bytes of data)
				# data is used to store information that is requested above
				fileWrite.write(data)
				recvCount += len(data) 	#i ncrease the count by number of read bytes
			
			#--- Download Complete ---
			return True



	def downloadFileChunked(self, fileName: str, savePath: str)-> bool:
		with open(savePath + ('/' if savePath else '') + (fileName if fileName else 'index.html'), "wb") as fileWrite:
			data = None
			flag = b''

			while (1):
				bytesToWriteHex = b''

				#Take the length of chunks in hex
				while (flag != b"\n"):
					data = self.s.recv(1)

					#Raise error if recv NOTHING
					if len(data) == 0:
						print("socket connection broken")
						self.closeConnection()
						return False

					flag = data
					if (flag != b"\r"):
						bytesToWriteHex += flag


				#Convert string to int
				if (bytesToWriteHex != b""):
					bytesToWriteInt = int(bytesToWriteHex.decode(), base=16)

				# 0 nghĩa là kết thúc file, đã tải xong
				if bytesToWriteInt == 0:
					return True

				#Write data
				recvCount = 0
				while(recvCount < bytesToWriteInt):
					data = self.s.recv(1)

					#Raise error if recv NOTHING
					if len(data) == 0:
						print("socket connection broken")
						self.closeConnection()
						return False
	
					fileWrite.write(data)
					recvCount += 1

				#To bypass /r/n at the end message
				data = self.s.recv(2)

				flag = ''


	def downloadFile(self, downloadPath: str(), fileName: str, savePath = "", attemps = 0) -> True:
		
		#----- if >= 3 attemps, proceed to break
		if (attemps == 3):
			print("Cannot download file", fileName)
			return False

		#Send Request
		self.sendRequest(downloadPath)
		
		#----- GET HEADER ------
		header = b''
		flag = b''
		while (flag != b"\r\n\r\n"):
			data = self.s.recv(1)

			#----- Error handling -----
			if len(data) == 0:
				print("recv 0 err")
				self.closeConnection()
				self.startConnection()
				return self.downloadFile(downloadPath, fileName, savePath, attemps + 1)
			
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
		if header.find(b'200 OK') == -1:
			print("Error while requesting file", fileName)
			print(header.decode())
			return False

		# if no err happens, then continue downloading
		#----- DECIDE DOWNLOAD MODE -----
		# if header has 'chunked' then call chunked
		if (header.find(b'chunked') != -1):
			return self.downloadFileChunked(fileName, savePath)
		else:
			#Get Content-Length from header
			contentLengthIndex = header.find(b'Content-Length:')
			n = header[contentLengthIndex + 16: header.find(b'\r\n', contentLengthIndex + 16)].decode()
			contentLength = int(n)
			return self.downloadFileCLength(fileName, savePath, contentLength)

		


	def downloadFolder(self, url):
		partsList = url.path.rstrip('/').split('/')
		domain = url.hostname

		#----- Create folder: domain_folderName ------
		downloadFolderName = domain + '_' + partsList[-1]
		if not os.path.exists(downloadFolderName): # Nếu folder tồn tại thì không tạo nữa
			os.mkdir(downloadFolderName)


		#----- DOWNLOAD index.html -----
		if (not self.downloadFile(url.path, 'index.html', downloadFolderName)):
			print("Cannot download index.html of a folder, exitting!")
			return False

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

		#----- Download complete-----
		return True



def handleConnection(address: str()):
	url = urlparse(address)

	#----- Creating ClientSocket object
	cs = ClientSocket()
	cs.HOST = url.hostname

	#----- CONNECT -----
	cs.startConnection()

	#----- URL là 1 file, 1 folder hay là thư mục gốc '/'? ------
	if len(url.path) > 1: #URL khác '' và '/'

		#URL chứa dấu '.' tức đây là URL tải 1 file
		if (url.path.find('.') == -1):
			return cs.downloadFolder(url)

		else:	# Tải 1 Folder
			return cs.downloadFile(url.path, url.hostname + '_' + url.path.rstrip('/').split('/')[-1])

	else:	#Với các request là "/" gốc thì mặc định tải và lưu thành file '<domain>_index.html'
		return cs.downloadFile('/', url.hostname + '_index.html')
