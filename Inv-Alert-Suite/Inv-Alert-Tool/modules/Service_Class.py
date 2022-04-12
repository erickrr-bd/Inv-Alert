from libPyLog import libPyLog
from io import open as open_io
from libPyUtils import libPyUtils
from os import system, path, remove
from libPyDialog import libPyDialog
from .Constants_Class import Constants

"""
Class that manages what is related to the Inv-Alert service.
"""
class Service:
	"""
	Attribute that stores an object of the libPyUtils class.
	"""
	__utils = None

	"""
	Attribute that stores an object of the libPyDialog class.
	"""
	__dialog = None

	"""
	Attribute that stores an object of the libPyLog class.
	"""
	__logger = None

	"""
	Attribute that stores an object of the Constants class.
	"""
	__constants = None

	"""
	Attribute that stores the method to be called when the user chooses the cancel option.
	"""
	__action_to_cancel = None


	def __init__(self, action_to_cancel):
		"""
		Method that corresponds to the constructor of the class.

		:arg action_to_cancel: Method to be called when the user chooses the cancel option.
		"""
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__action_to_cancel = action_to_cancel
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, action_to_cancel)
		self.__logger = libPyLog(self.__constants.NAME_FILE_LOG, self.__constants.NAME_LOG, self.__constants.USER, self.__constants.GROUP)


	def startService(self):
		"""
		Method to start the Inv-Alert service.
		"""
		result = system("systemctl start inv-alert.service")
		if int(result) == 0:
			self.__logger.createApplicationLog("Inv-Alert service started", 1)
			self.__dialog.createMessageDialog("\nInv-Alert service started.", 7, 50, "Notification Message")
		elif int(result) == 1280:
			self.__logger.createApplicationLog("Failed to start Inv-Alert service. Not found.", 3)
			self.__dialog.createMessageDialog("\nFailed to start Inv-Alert service. Not found.", 7, 50, "Error Message")
		self.__action_to_cancel()


	def restartService(self):
		"""
		Method to restart the Inv-Alert service.
		"""
		result = system("systemctl restart inv-alert.service")
		if int(result) == 0:
			self.__logger.createApplicationLog("Inv-Alert service restarted", 1)
			self.__dialog.createMessageDialog("\nInv-Alert service restarted.", 7, 50, "Notification Message")
		elif int(result) == 1280:
			self.__logger.createApplicationLog("Failed to restart Inv-Alert service. Not found.", 3)
			self.__dialog.createMessageDialog("\nFailed to restart Inv-Alert service. Not found.", 7, 50, "Error Message")
		self.__action_to_cancel()


	def stopService(self):
		"""
		Method to stop the Inv-Alert service.
		"""
		result = system("systemctl stop inv-alert.service")
		if int(result) == 0:
			self.__logger.createApplicationLog("Inv-Alert service stopped", 1)
			self.__dialog.createMessageDialog("\nInv-Alert service stopped.", 7, 50, "Notification Message")
		elif int(result) == 1280:
			self.__logger.createApplicationLog("Failed to stop Inv-Alert service. Not found.", 3)
			self.__dialog.createMessageDialog("\nFailed to stop Inv-Alert service. Not found.", 7, 50, "Error Message")
		self.__action_to_cancel()


	def getActualStatusService(self):
		"""
		Method to get the current status of the Inv-Alert service.
		"""
		if path.exists("/tmp/inv_alert.status"):
			remove("/tmp/inv_alert.status")
		system('(systemctl is-active --quiet inv-alert.service && echo "Inv-Alert service is running!" || echo "Inv-Alert service is not running!") >> /tmp/inv_alert.status')
		system('echo "Detailed service status:" >> /tmp/inv_alert.status')
		system('systemctl -l status inv-alert.service >> /tmp/inv_alert.status')
		with open_io("/tmp/inv_alert.status", 'r', encoding = 'utf-8') as status_file:
			self.__dialog.createScrollBoxDialog(status_file.read(), 15, 70, "Inv-Alert Service Status")
		self.__action_to_cancel()