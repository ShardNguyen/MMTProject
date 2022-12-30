#----- SOCKET -----
import ClientSocket

#----- argv -----
import sys

#----- threading -----
import threading


if __name__ == "__main__":

	#---- Không có link nào được truyền vào-----
	if len(sys.argv) == 1:
		address = input("Enter address: ")
		ClientSocket.handleConnection(address)
	
	#----- Có 1 link -----
	elif len(sys.argv) == 2:
		ClientSocket.handleConnection(sys.argv[1])
	
	#----- Có nhiều link -----
	else:
		for i in range(1, len(sys.argv)):
			x = threading.Thread(target=ClientSocket.handleConnection, args=(sys.argv[i],), daemon=False)
			x.start()


