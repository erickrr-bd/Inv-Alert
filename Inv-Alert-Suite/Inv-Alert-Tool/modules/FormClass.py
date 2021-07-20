import re
from os import path
from sys import exit
from dialog import Dialog
from modules.UtilsClass import Utils
from modules.InventoriesClass import Inventories
from modules.ConfigurationClass import Configuration

"""
"""
class FormDialogs:
	"""
	Property that stores an object of type Dialog.
	"""
	d = None

	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Property that stores an object of type Configuration.
	"""
	configuration = None

	"""
	Property that stores an object of type Inventories.
	"""
	inventories = None

	"""
	Constructor for the FormDialogs class.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	"""
	def __init__(self):
		self.utils = Utils(self)
		self.inventories = Inventories(self)
		self.d = Dialog(dialog = "dialog")
		self.configuration = Configuration(self)
		self.d.set_background_title("INV-ALERT-TOOL")

	"""
	Method that generates the menu interface.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	options -- List of options that make up the menu.
	title -- Title that will be given to the interface and that will be shown to the user.

	Return:
	tag_mm -- The option chosen by the user.
	"""
	def getMenu(self, options, title):
		code_mm, tag_mm = self.d.menu("Choose an option", choices = options,title = title)
		if code_mm == self.d.OK:
			return tag_mm
		if code_mm == self.d.CANCEL:
			exit(0)

	"""
	Method that generates the interface with a list of options, where only one can be chosen.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	options -- List of options that make up the interface.
	title -- Title that will be given to the interface and that will be shown to the user.

	Return:
	tag_rl -- The option chosen by the user.
	"""
	def getDataRadioList(self, text, options, title):
		while True:
			code_rl, tag_rl = self.d.radiolist(
					  text,
					  width = 65,
					  choices = options,
					  title = title)
			if code_rl == self.d.OK:
				if len(tag_rl) == 0:
					self.d.msgbox("\nSelect at least one option.", 7, 50, title = "Error Message")
				else:
					return tag_rl
			if code_rl == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface with a list of options,
	where you can choose one or more.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	options -- List of options that make up the interface.
	title -- Title that will be given to the interface and that
			 will be shown to the user.

	Return:
	tag_cl -- List with the chosen options.
	"""
	def getDataCheckList(self, text, options, title):
		while True:
			code_cl, tag_cl = self.d.checklist(
					 text,
					 width = 75,
					 choices = options,
					 title = title)
			if code_cl == self.d.OK:
				if len(tag_cl) == 0:
					self.d.msgbox("\nSelect at least one option.", 7, 50, title = "Error Message")
				else:
					return tag_cl
			if code_cl == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the message interface with scroll box.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	title -- Title that will be given to the interface and that
			 will be shown to the user.
	"""
	def getScrollBox(self, text, title):
		code_sb = self.d.scrollbox(text, 15, 70, title = title)
		if code_sb == self.d.OK:
			self.mainMenu()

	"""
	Method that generates the interface for entering decimal or
	floating type data.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the
					 user in the interface.

	Return:
	tag_nd -- Decimal value entered.
	"""
	def getDataNumberDecimal(self, text, initial_value):
		decimal_reg_exp = re.compile(r'^[1-9](\.[0-9]+)?$')
		while True:
			code_nd, tag_nd = self.d.inputbox(text, 10, 50, initial_value)
			if code_nd == self.d.OK:
				if(not self.utils.validateRegularExpression(decimal_reg_exp, tag_nd)):
					self.d.msgbox("\nInvalid data entered. Required value (decimal or float).", 8, 50, title = "Error Message")
				else:
					if(float(tag_nd) < 7.0 or float(tag_nd) > 7.13):
						self.d.msgbox("\nElasticSearch version not valid. Versions supported between 7.0 - 7.13.", 8, 50, title = "Error Message")
					else:
						return tag_nd
			if code_nd == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface for the entry of data of type IP address.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the user in the interface.

	Return:
	tag_ip -- IP address entered.
	"""
	def getDataIP(self, text, initial_value):
		ip_reg_exp = re.compile(r'^(?:(?:[1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}(?:[1-9]?[0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$|^localhost$')
		while True:
			code_ip, tag_ip = self.d.inputbox(text, 10, 50, initial_value)
			if code_ip == self.d.OK:
				if(not self.utils.validateRegularExpression(ip_reg_exp, tag_ip)):
					self.d.msgbox("\nInvalid data entered. Required value (IP address).", 8, 50, title = "Error message")
				else:
					return tag_ip
			if code_ip == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface for entering data type communication port.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the user in the interface.

	Return:
	tag_port -- Port entered.
	"""
	def getDataPort(self, text, initial_value):
		port_reg_exp = re.compile(r'^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$')
		while True:
			code_port, tag_port = self.d.inputbox(text, 10, 50, initial_value)
			if code_port == self.d.OK:
				if(not self.utils.validateRegularExpression(port_reg_exp, tag_port)):
					self.d.msgbox("\nInvalid data entered. Required value (0 - 65535).", 8, 50, title = "Error message")
				else:
					return tag_port
			if code_port == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface for entering directory
	or file name data.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the
					 user in the interface.

	Return:
	tag_fname -- File or directory name entered.
	"""
	def getDataNameFolderOrFile(self, text, initial_value):
		name_file_reg_exp = re.compile(r'^[^\\/?%*:|"<>]+$')
		while True:
			code_fname, tag_fname = self.d.inputbox(text, 10, 50, initial_value)
			if code_fname == self.d.OK:
				if(not self.utils.validateRegularExpression(name_file_reg_exp, tag_fname)):
					self.d.msgbox("\nInvalid data entered. Required value (folder name).", 8, 50, title = "Error message")
				else:
					return tag_fname
			if code_fname == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface for entering text type
	data.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the
					 user in the interface.

	Return:
	tag_input -- Text entered.
	"""
	def getDataInputText(self, text, initial_value):
		while True:
			code_input, tag_input = self.d.inputbox(text, 10, 50, initial_value)
			if code_input == self.d.OK:
				if tag_input == "":
					self.d.msgbox("\nInvalid data entered. Required value (not empty).", 8, 50, title = "Error message")
				else:
					return tag_input
			if code_input == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates the interface for entering password
	type data.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	initial_value -- Default value that will be shown to the
					 user in the interface.

	Return:
	tag_pass -- Password entered.
	"""
	def getDataPassword(self, text, initial_value):
		while True:
			code_pass, tag_pass = self.d.passwordbox(text, 10, 50, initial_value, insecure = True)
			if code_pass == self.d.OK:
				if tag_pass == "":
					self.d.msgbox("\nInvalid data entered. Required value (not empty).", 8, 50, title = "Error message")
				else:
					return tag_pass
			if code_pass == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that generates an interface where it is allowed
	to select a time.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text displayed on the interface.
	hour -- Chosen hour.
	minutes -- Chosen minutes.

	Return:
	tag_time -- Chosen time.
	"""
	def getDataTime(self, text, hour, minutes):
		code_time, tag_time = self.d.timebox(text,
											hour = hour,
											minute = minutes,
											second = 00)
		if code_time == self.d.OK:
			return tag_time
		if code_time == self.d.CANCEL:
			self.mainMenu()

	"""
	Method that generates the interface for entering
	questioning type data with two possible yes or no values.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	text -- Text that will be shown to the user.
	title -- Title that will be given to the interface and that
			 will be shown to the user.

	Return:
	tag_yesorno -- Chosen option (yes or no).
	"""
	def getDataYesOrNo(self, text, title):
		tag_yesorno = self.d.yesno(text, 10, 50, title = title)
		return tag_yesorno

	"""
	Method generated by the interface to select a file or 
	directory.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	initial_path -- Initial path where the interface will place
					the user.
	title -- Title that will be given to the interface and that
			 will be shown to the user.

	Return:
	tag_df -- Path of the selected file.
	"""
	def getFileOrDirectory(self, initial_path, title):
		while True:
			code_fd, tag_df = self.d.fselect(initial_path, 8, 50, title = title)
			if code_fd == self.d.OK:
				if tag_df == "":
					self.d.msgbox("\nSelect a file. Required value (PEM file).", 8, 50, title = "Error Message")
				else:
					return tag_df
			if code_fd == self.d.CANCEL:
				self.mainMenu()

	"""
	Method that defines the action to be performed on the Inv-Alert configuration file (creation or modification).

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	"""
	def defineConfiguration(self):
		options_conf_false = [("Create", "Create the configuration file", 0)]

		options_conf_true = [("Modify", "Modify the configuration file", 0)]
		
		try:
			if not path.exists(self.configuration.conf_file):
				opt_conf_false = self.getDataRadioList("Select a option:", options_conf_false, "Configuration Options")
				if opt_conf_false == "Create":
					self.configuration.createConfiguration()
			else:
				opt_conf_true = self.getDataRadioList("Select a option:", options_conf_true, "Configuration Options")
				if opt_conf_true == "Modify":
					self.configuration.updateConfiguration()
		except TypeError as exception:
			self.utils.createInvAlertToolLog(exception, 4)
			self.d.msgbox("\nAn error has occurred. For more information, see the logs.", 8, 50, title = "Error Message")
			self.mainMenu()

	"""
	Method that defines the menu of options related to
	inventories.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	"""
	def inventoriesMenu(self):
		options_im = [("1", "Create Inventory"),
					  ("2", "Update Inventory"),
					  ("3", "Delete Inventory"),
					  ("4", "Show Inventories")]

		option_im = self.getMenu(options_im, "Inventories Menu")
		self.switchImenu(int(option_im))

	"""
	Method that displays a message on the screen with 
	information about the application.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	"""
	def getAbout(self):
		message = "\nCopyright@2021 Tekium. All rights reserved.\nInv-Alert v3.0\nAuthor: Erick Rodriguez\nEmail: erickrr.tbd93@gmail.com, erodriguez@tekium.mx\n" + "License: GPLv3\n\nInv-Alert is a tool that allows you to obtain the daily inventory\nof equipment found in a specific ElasticSearch index, and send it\nvia Telegram at a configurable time."
		self.getScrollBox(message, "About")

	"""
	Method that launches an action based on the option
	chosen in the main menu.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	option -- Chosen option.
	"""
	def switchMmenu(self, option):
		if option == 1:
			self.defineConfiguration()
		if option == 2:
			self.inventoriesMenu()
		#if option == 3:
		#	self.getDeleteSnapshot()
		if option == 4:
			self.getAbout()
		if option == 5:
			exit(0)

	"""
	Method that launches an action based on the option
	chosen in the inventories menu.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	option -- Chosen option.
	"""
	def switchImenu(self, option):
		if option == 1:
			self.inventories.createInventory()

	"""
	Method that defines the menu on the actions to be
	carried out in the main menu.

	Parameters:
	self -- An instantiated object of the FormDialogs class.
	"""
	def mainMenu(self):
		options_mm = [("1", "Inv-Alert Configuration"),
					  ("2", "Inventories"),
					  ("3", "Inv-Alert Service"),
					  ("4", "About"),
					  ("5", "Exit")]

		option_mm = self.getMenu(options_mm, "Main Menu")
		self.switchMmenu(int(option_mm))