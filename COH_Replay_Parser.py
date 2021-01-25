import sys
import logging
from functools import partial


class COH_Replay_Parser:
	"""Parses a company of heroes 1 replay to extract as much useful information from it as possible."""

	def __init__(self, filePath = None) -> None:


		self.filePath = filePath
		self.fileName = None
		self.fileVersion = None
		self.chunkyHeaderLength = None
		self.chunkyVersion = None # 3
		
		self.replayVersion = None
		self.localDate = None
		self.unknownDate = None
		self.replayName = None
		self.otherVariables = {}
		self.modName = None
		self.mapName = None
		self.mapDescription = None
		self.mapFileName = None
		self.mapWidth = None
		self.mapHeight = None
		self.playerList = []

		self.data = None
		self.dataIndex = 0

		if filePath:
			self.load(self.filePath)

	def read_UnsignedLong4Bytes(self) -> int:
		"""Reads 4 bytes as an unsigned long int."""
		try:
			if self.data:
				fourBytes = bytearray(self.data[self.dataIndex:self.dataIndex+4])
				self.dataIndex += 4
				theInt = int.from_bytes(fourBytes, byteorder='little', signed=False)
				return theInt
		except Exception as e:
			logging.error("Failed to read 4 bytes")
			logging.exception("Stack Trace: ")

	def read_Bytes(self, numberOfBytes):
		"""reads a number of bytes from the data array"""
		try:
			if self.data:
				output = bytearray(self.data[self.dataIndex:self.dataIndex+numberOfBytes])
				self.dataIndex += numberOfBytes
				return output
		except Exception as e:
			logging.error("Failed to Read bytes")
			logging.exception("Stack Trace: ")


	def read_LengthString(self):
		"""Reads the first 4 bytes containing the string length and then the rest of the string."""
		try:
			if self.data:
				stringLength = self.read_UnsignedLong4Bytes()
				theString = self.read_2ByteString(stringLength =stringLength)
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")

	def read_2ByteString(self, stringLength=0 ) -> str:
		"""Reads a 2byte encoded little-endian string of specified length."""
		try:
			if self.data:
				theBytes = bytearray(self.data[self.dataIndex:self.dataIndex+(stringLength*2)])
				self.dataIndex += stringLength*2
				theString = theBytes.decode('utf-16le')
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")            

	def read_LengthASCIIString(self) -> str:
		"""Reads ASCII string, the length defined by the first four bytes."""
		try:
			if self.data:
				stringLength = self.read_UnsignedLong4Bytes()
				theString = self.read_ASCIIString(stringLength=stringLength)
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_ASCIIString(self, stringLength=0) -> str:
		"""Reads a byte array of spcified length and attempts to convert it into a string."""
		try:
			if self.data:
				theBytes = bytearray(self.data[self.dataIndex:self.dataIndex+stringLength])
				self.dataIndex += stringLength
				theString = theBytes.decode('ascii')
				return theString
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_NULLTerminated_2ByteString(self) -> str:
		"""Reads a Utf-16 little endian character string until the first two byte NULL value."""
		try:
			if self.data:
				characters = ""
				for character in iter(partial(self.read_Bytes, 2) , bytearray(b"\x00\x00")):
					characters += bytearray(character).decode('utf-16le')
				return characters    
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def read_NULLTerminated_ASCIIString(self) -> str:
		"""Reads a byte array until the first NULL and converts to a string."""
		try:
			if self.data:
				characters = ""
				for character in iter(partial(self.read_Bytes, 1) , bytearray(b"\x00")):
					characters += bytearray(character).decode('ascii')
				return characters  
		except Exception as e:
			logging.error("Failed to read a string of specified length")
			logging.exception("Stack Trace: ")  

	def seek(self, numberOfBytes, relative = 0):
		"""Moves the file index a number of bytes forward or backward"""
		try:
			numberOfBytes = int(numberOfBytes)
			relative = int(relative)
			if relative == 0:
				assert(0 <= numberOfBytes <= len(self.data))
				self.dataIndex = numberOfBytes
			if relative == 1:
				assert(0 <= (numberOfBytes+self.dataIndex) <= len(self.data))
				self.dataIndex += numberOfBytes
			if relative == 2:
				assert(0 <= (len(self.data) - numberOfBytes) <= len(self.data))
				self.dataIndex = len(self.data) - numberOfBytes
		except Exception as e:
			logging.error("Failed move file Index")
			logging.exception("Stack Trace: ")
			return None          



	def load(self, filePath = ""):
		with open(filePath, "rb") as fileHandle:
			self.data = fileHandle.read()
		self.processData()

	def processData(self):

		#Process the file Header
		self.fileVersion = self.read_UnsignedLong4Bytes()
		cohrec = self.read_ASCIIString(stringLength= 8)
		print("cohrec : {}".format(cohrec))

		self.localDate = self.read_NULLTerminated_2ByteString()
		self.seek(2, 1) #move extra two bytes to keep in 4 byte frame of reference at end of string
		print("dataIndex : {}".format(self.dataIndex))
		for x in range(7):
			print(self.read_UnsignedLong4Bytes())
		#self.chunkyHeaderLength = self.read_UL4(fileHandle = fileHandle)
		firstRelicChunkyAddress = self.dataIndex
		relicChunky = self.read_ASCIIString(stringLength=12)
		#print("relicChunky : {}".format(relicChunky))
		unknown = self.read_UnsignedLong4Bytes()
		self.chunkyVersion = self.read_UnsignedLong4Bytes() # 3
		unknown = self.read_UnsignedLong4Bytes()
		self.chunkyHeaderLength = self.read_UnsignedLong4Bytes()
		self.seek(-28,1) # sets file pointer back to start of relic chunky
		self.seek(self.chunkyHeaderLength, 1) # seeks to begining of FOLDPOST

		self.seek(firstRelicChunkyAddress, 0)
		self.seek(96,1) # move pointer to the position of the second relic chunky
		secondRelicChunkyAddress = self.dataIndex

		relicChunky = self.read_ASCIIString(stringLength=12)

		unknown = self.read_UnsignedLong4Bytes()
		chunkyVersion = self.read_UnsignedLong4Bytes() # 3
		unknown = self.read_UnsignedLong4Bytes()
		chunkLength = self.read_UnsignedLong4Bytes()
		
		self.seek(secondRelicChunkyAddress, 0)
		self.seek(chunkLength, 1) # seek to position of first viable chunk

		self.parseChunk(0)


	def parseChunk(self, level):

		print("LEVEL : {}".format(level))
		
		
		print("dataIndex {} ".format(self.dataIndex))
		chunkType = self.read_ASCIIString(stringLength= 8) # Reads FOLDFOLD, FOLDDATA, DATASDSC, DATAINFO etc
		print("chunkType : {}".format(chunkType))

		chunkVersion = self.read_UnsignedLong4Bytes()
		chunkLength = self.read_UnsignedLong4Bytes()
		chunkNameLength = self.read_UnsignedLong4Bytes()
		print("dataIndex {} ".format(self.dataIndex))
		self.seek(8,1)
		print("dataIndex {} ".format(self.dataIndex))
		chunkName = ""
		if chunkNameLength > 0:
			chunkName = self.read_ASCIIString(stringLength=chunkNameLength)
		
		print("chunkVersion {}, chunkLength {}, chunkNameLength {}, chunkName {}".format(chunkVersion, chunkLength, chunkNameLength, chunkName))

		chunkStart = self.dataIndex

		#Here we start a recusive loop
		if (chunkType.startswith("FOLD")):
			print("STATS WITH FOLD")
			while (self.dataIndex < (chunkStart + chunkLength )):
				self.parseChunk(level=level+1)

		if (chunkType == "DATASDSC") and (int(chunkVersion) == 2004):

			unknown = self.read_UnsignedLong4Bytes()
			self.unknownDate = self.read_LengthString()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			self.modName = self.read_LengthASCIIString() 
			self.mapFileName = self.read_LengthASCIIString()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			self.mapName = self.read_LengthString()
			unknown = self.read_UnsignedLong4Bytes()
			self.mapDescription = self.read_LengthString()
			unknown = self.read_UnsignedLong4Bytes()
			self.mapWidth = self.read_UnsignedLong4Bytes()
			self.mapHeight = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes()
			unknown = self.read_UnsignedLong4Bytes() 

			if(chunkType == "DATABASE") and (int(chunkVersion == 11)):

				print("Got to DATABASE")

				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()
				
				variableCount = self.read_UnsignedLong4Bytes()
				for i in range(variableCount):
					variableValue = self.read_UnsignedLong4Bytes()
					variableName = self.read_LengthString(4)[::-1]
					self.otherVariables[variableName] = variableValue
				
				unknown = self.read_Bytes(1)
				self.replayName = self.read_LengthString()
				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()
				unknown = self.read_UnsignedLong4Bytes()

			if(chunkType == "DATAINFO") and (chunkVersion == 6):

				print("got to FATAINFO")
				userName = self.read_LengthString()
				self.read_UnsignedLong4Bytes()
				self.read_UnsignedLong4Bytes()
				faction = self.read_LengthString()
				self.read_UnsignedLong4Bytes()
				self.read_UnsignedLong4Bytes()
				self.playerList.append((userName,faction))


		self.seek(chunkStart + chunkLength, 0)

	def __str__(self) -> str:
		output = "Data:\n"
		output += "fileVersion : {}\n".format(self.fileVersion)
		output += "chunkyHeaderLength : {}\n".format(self.chunkyHeaderLength)
		output += "replayVersion : {}\n".format(self.replayVersion)
		output += "chunkyVersion : {}\n".format(self.chunkyVersion)
		output += "fileName : {}\n".format(self.fileName)
		output += "localDate : {}\n".format(self.localDate)
		output += "unknownDate : {}\n".format(self.unknownDate)
		output += "replayName : {}\n".format(self.replayName)
		output += "otherVariables : {}\n".format(self.otherVariables)
		output += "modName : {}\n".format(self.modName)
		output += "mapName : {}\n".format(self.mapName)
		output += "mapDescription : {}\n".format(self.mapDescription)
		output += "mapFileName : {}\n".format(self.mapFileName)
		output += "mapWidth : {}\n".format(self.mapWidth)
		output += "mapHeight : {}\n".format(self.mapHeight)
		output += "playerList : {}\n".format(self.playerList)
		return output




# Program Entry Starts here
# Default error logging log file location:
for handler in logging.root.handlers[:]:
	logging.root.removeHandler(handler)
logging.basicConfig(format='%(asctime)s (%(threadName)-10s) [%(levelname)s] %(message)s', filename= 'Errors.log',filemode = "w", level=logging.INFO)

myCOHReplayParser = COH_Replay_Parser("temp.rec")
print(myCOHReplayParser)
