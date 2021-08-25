from pwd import getpwnam
from datetime import date
from os import path, chown
from hashlib import sha256
from base64 import b64decode
from Crypto.Cipher import AES
from yaml import safe_load, safe_dump
from Crypto.Util.Padding import unpad
from logging import getLogger, INFO, Formatter, FileHandler

"""
Class that allows managing all the utilities that are used for
the operation of the application.
"""
class Utils:
	"""
	Property that stores the passphrase that will be used for 
	the encryption/decryption process.
	"""
	passphrase = None

	"""
	Constructor for the Utils class.

	Parameters:
	self -- An instantiated object of the Utils class.
	"""
	def __init__(self):
		self.passphrase = self.getPassphrase()

	"""
	Method that obtains and stores the content of a YAML file
	in a variable.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_file_yaml -- YAML file path.
	mode -- Mode in which the YAML file will be opened.

	Return:
	data_file_yaml -- Variable that stores the content of the
					  YAML file.

	Exceptions:
	IOError -- It is an error raised when an input/output
	           operation fails.
	"""
	def readYamlFile(self, path_file_yaml, mode):
		try:
			with open(path_file_yaml, mode) as file_yaml:
				data_file_yaml = safe_load(file_yaml)
		except IOError as exception:
			self.createInvAlertLog(exception, 3)
			print("\nError opening or reading the YAML file. For more information, see the logs.")
		else:
			return data_file_yaml

	"""
	Method that creates a YAML file.

	Parameters:
	self -- An instantiated object of the Utils class.
	data -- Information that will be stored in the YAML file.
	path_file_yaml -- YAML file path.
	mode -- Mode in which the YAML file will be opened.

	Exceptions:
	IOError -- It is an error raised when an input/output
	           operation fails.
	"""
	def createYamlFile(self, data, path_file_yaml, mode):
		try:
			with open(path_file_yaml, mode) as file_yaml:
				safe_dump(data, file_yaml, default_flow_style = False)
			self.ownerChange(path_file_yaml)
		except IOError as exception:
			self.createInvAlertLog(exception, 3)
			print("\nError creating YAML file. For more information, see the logs.")

	"""
	Method that defines a directory based on the main Inv-Alert
	directory.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_dir -- Directory that is added to the main Inv-Alert 
	            directory.

	Return:
	path_final -- Defined final path.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	TypeError -- Raised when an operation or function is applied
				 to an object of inappropriate type. The associated
				 value is a string giving details about the type 
				 mismatch.
	"""
	def getPathInvAlert(self, path_dir):
		path_main = "/etc/Inv-Alert-Suite/Inv-Alert"
		try:
			path_final = path.join(path_main, path_dir)
		except (OSError, TypeError) as exception:
			self.createInvAlertLog(exception, 3)
			print("\nAn error has occurred. For more information, see the logs.")
		else:
			return path_final

	"""
	Method that obtains the passphrase used for the process of
	encrypting and decrypting a file.

	Parameters:
	self -- An instantiated object of the Utils class.

	Return:
	pass_key -- Passphrase in a character string.

	Exceptions:
	FileNotFoundError -- This is an exception in python and it
						 comes when a file does not exist
						 and we want to use it. 
	"""
	def getPassphrase(self):
		try:
			file_key = open(self.getPathInvAlert('conf') + '/key','r')
			pass_key = file_key.read()
			file_key.close()
		except FileNotFoundError as exception:
			self.createInvAlertLog(exception, 3)
			print("\nError opening or reading the Key file. For more information, see the logs.")
		else:
			return pass_key

	"""
	Method that changes an owner path, by inv_alert user and 
	group.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_to_change -- Directory that will change owner.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def ownerChange(self, path_to_change):
		try:
			uid = getpwnam('inv_alert').pw_uid
			gid = getpwnam('inv_alert').pw_gid
			chown(path_to_change, uid, gid)
		except OSError as exception:
			self.createInvAlertLog(exception, 3)
			print("\nFailed to change owner path. For more information, see the logs.")

	"""
	Method that decrypts a text string.

	Parameters:
	self -- An instantiated object of the Utils class.
	text_encrypt -- Text to decipher.
	form_dialog -- A FormDialogs class object.

	Return:
	Character string with decrypted text.

	Exceptions:
	binascii.Error -- Is raised if were incorrectly padded or
					  if there are non-alphabet characters
					  present in the string. 
	"""
	def decryptAES(self, text_encrypt):
		try:
			key = sha256(self.passphrase.encode()).digest()
			text_encrypt = b64decode(text_encrypt)
			IV = text_encrypt[:AES.block_size]
			aes = AES.new(key, AES.MODE_CBC, IV)
		except binascii.Error as exception:
			self.createInvAlertLog(exception, 3)
			print("\nFailed to decrypt the data. For more information, see the logs.")
		else:
			return unpad(aes.decrypt(text_encrypt[AES.block_size:]), AES.block_size)

	"""
	Method that writes the logs generated by the application in
	a file.

	Parameters:
	self -- An instantiated object of the Utils class.
	message -- Message to be shown in the log.
	type_log -- Type of log to write.
	"""
	def createInvAlertLog(self, message, type_log):
		name_log = '/var/log/Inv-Alert/inv-alert-log-' + str(date.today()) + '.log'
		logger = getLogger('Inv_Alert_Log')
		logger.setLevel(INFO)
		fh = FileHandler(name_log)
		if (logger.hasHandlers()):
   	 		logger.handlers.clear()
		formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
		if type_log == 1:
			logger.info(message)
		if type_log == 2:
			logger.warning(message)
		if type_log == 3:
			logger.error(message)
		self.ownerChange(name_log)

