import os
import pwd
import logging
from datetime import date
from Crypto import Random
from hashlib import sha256
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad

"""
Class that allows managing all the utilities that are used for
the operation of the application.
"""
class Utils:
	"""
	Property that stores an object of type FormDialogs.
	"""
	form_dialog = None

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
	def __init__(self, form_dialog):
		self.form_dialog = form_dialog
		self.passphrase = self.getPassphrase()

	"""
	Method that defines a directory based on the main Inv-Alert
	directory.

	Parameters:
	self -- An instantiated object of the Utils class.
	path_dir -- Directory that is added to the main Inv-Alert 
	            directory.
	form_dialog -- A FormDialogs class object.

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
			path_final = os.path.join(path_main, path_dir)
		except (OSError, TypeError) as exception:
			self.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("\nAn error has occurred. For more information, see the logs.", 8, 50, title = "Error Message")
			self.form_dialog.mainMenu()
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
	FileNotFoundError -- his is an exception in python and it
	comes when a file does not exist and we want to use it. 
	"""
	def getPassphrase(self):
		try:
			file_key = open(self.getPathInvAlert('conf') + '/key','r')
			pass_key = file_key.read()
			file_key.close()
		except FileNotFoundError as exception:
			self.createInvAlertToolLog(exception, 4)
			self.form_dialog.d.msgbox("\nError opening or reading the Key file. For more information, see the logs.", 8, 50, title = "Error message")
			self.form_dialog.mainMenu()
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
			uid = pwd.getpwnam('inv_alert').pw_uid
			gid = pwd.getpwnam('inv_alert').pw_gid
			os.chown(path_to_change, uid, gid)
		except OSError as exception:
			self.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("\nFailed to change owner path. For more information, see the logs.", 8, 50, title = "Error Message")
			self.form_dialog.mainMenu()

	"""
	Method that validates an entered value based on a defined
	regular expression.

	Parameters:
	self -- An instantiated object of the Utils class.
	regular_expression -- Regular expression with which the 
						  data will be validated.
	data_entered -- Data to be validated.

	Return:
	If the data entered is valid or not.
	"""
	def validateRegularExpression(self, regular_expression, data_entered):
		if(not regular_expression.match(data_entered)):
			return False
		return True

	"""
	Method that encrypts a text string.

	Parameters:
	self -- An instantiated object of the Utils class.
	text -- Text to encrypt.
	form_dialog -- A FormDialogs class object.

	Return:
	Encrypted text.

	Exceptions:
	binascii.Error -- Is raised if were incorrectly padded or
					  if there are non-alphabet characters
					  present in the string. 
	"""
	def encryptAES(self, text):
		try:
			text_bytes = bytes(text, 'utf-8')
			key = sha256(self.passphrase.encode()).digest()
			IV = Random.new().read(AES.block_size)
			aes = AES.new(key, AES.MODE_CBC, IV)
		except Exception as exception:
			self.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("\nFailed to encrypt the data. For more information, see the logs.", 8, 50, title = "Error message")
			self.form_dialog.mainMenu()
		else:
			return b64encode(IV + aes.encrypt(pad(text_bytes, AES.block_size)))

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
			self.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("\nFailed to decrypt the data. For more details, see the logs.", 8, 50, title = "Error message")
			self.form_dialog.mainMenu()
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
	def createInvAlertToolLog(self, message, type_log):
		name_log = '/var/log/Inv-Alert/inv-alert-tool-log-' + str(date.today()) + '.log'
		logger = logging.getLogger('Inv_Alert_Tool_Log')
		logger.setLevel(logging.INFO)
		fh = logging.FileHandler(name_log)
		logger.addHandler(fh)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		fh.setFormatter(formatter)
		logger.addHandler(fh)
		if type_log == 1:
			logger.info(message)
		if type_log == 2:
			logger.warning(message)
		if type_log == 3:
			logger.error(message)
		self.ownerChange(name_log)