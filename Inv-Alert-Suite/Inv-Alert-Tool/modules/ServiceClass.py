from io import open as open_io
from os import system, path, remove
from modules.UtilsClass import Utils

"""
Class that manages everything related to the Inv-Alert
service.
"""
class Service:
	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Property that stores an object of type FormDialogs.
	"""
	form_dialog = None

	"""
	Constructor for the Service class.

	Parameters:
	self -- An instantiated object of the Service class.
	"""
	def __init__(self, form_dialog):
		self.form_dialog = form_dialog
		self.utils = Utils(form_dialog)

	"""
	Method that starts the Inv-Alert service.

	Parameters:
	self -- An instantiated object of the Service class.
	"""
	def startService(self):
		result = system("systemctl start inv-alert.service")
		if int(result) == 0:
			self.utils.createInvAlertToolLog("Inv-Alert service started", 1)
			self.form_dialog.d.msgbox("\nInv-Alert service started.", 7, 50, title = "Notification message")
		if int(result) == 1280:
			self.utils.createInvAlertToolLog("Failed to start inv-alert.service. Service not found.", 3)
			self.form_dialog.d.msgbox("\nFailed to start inv-alert.service. Service not found.", 7, 50, title = "Error message")
		self.form_dialog.mainMenu()
			
	"""
	Method that restarts the Inv-Alert service.

	Parameters:
	self -- An instantiated object of the Service class.
	"""
	def restartService(self):
		result = system("systemctl restart inv-alert.service")
		if int(result) == 0:
			self.utils.createInvAlertToolLog("Inv-Alert service restarted", 1)
			self.form_dialog.d.msgbox("\nInv-Alert service restarted.", 7, 50, title = "Notification message")
		if int(result) == 1280:
			self.utils.createInvAlertToolLog("Failed to restart inv-alert.service. Service not found.", 3)
			self.form_dialog.d.msgbox("\nFailed to restart inv-alert.service. Service not found", 7, 50, title = "Error message")
		self.form_dialog.mainMenu()

	"""
	Method that stops the Inv-Alert service.

	Parameters:
	self -- An instantiated object of the Service class.
	"""
	def stopService(self):
		result = system("systemctl stop inv-alert.service")
		if int(result) == 0:
			self.utils.createInvAlertToolLog("Inv-Alert service stopped", 1)
			self.form_dialog.d.msgbox("\nInv-Alert service stopped.", 7, 50, title = "Notification message")	
		if int(result) == 1280:
			self.utils.createInvAlertToolLog("Failed to stop inv-alert.service: Service not found", 3)
			self.form_dialog.d.msgbox("\nFailed to stop inv-alert.service. Service not found.", 7, 50, title = "Error message")
		self.form_dialog.mainMenu()

	"""
	Method that obtains the status of the Inv-Alert service.

	Parameters:
	self -- An instantiated object of the Service class.
	"""
	def getStatusService(self):
		if path.exists('/tmp/inv_alert.status'):
			remove('/tmp/inv_alert.status')
		system('(systemctl is-active --quiet inv-alert.service && echo "Inv-Alert service is running!" || echo "Inv-Alert service is not running!") >> /tmp/inv_alert.status')
		system('echo "Detailed service status:" >> /tmp/inv_alert.status')
		system('systemctl -l status inv-alert.service >> /tmp/inv_alert.status')
		with open_io('/tmp/inv_alert.status', 'r', encoding = 'utf-8') as file_status:
			self.form_dialog.getScrollBox(file_status.read(), title = "Status Service")