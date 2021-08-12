from shutil import rmtree
from datetime import datetime
from os import path, scandir, rename
from modules.UtilsClass import Utils

"""
Class that allows you to manage everything related to
inventories.
"""
class Inventories:
	"""
	Property that stores an object of type FormDialogs.
	"""
	form_dialog = None

	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Property that stores the path where inventories are
	stored.
	"""
	path_inventories = None

	"""
	Property that stores the options for how often the
	inventory will be fetched.
	"""
	options_frequency_inventory = [["Daily", "Daily execution", 0]]

	"""
	Constructor for the Inventories class.

	Parameters:
	self -- An instantiated object of the Inventories class.
	"""
	def __init__(self, form_dialog):
		self.form_dialog = form_dialog
		self.utils = Utils(form_dialog)
		aux_folder_inv = self.utils.readYamlFile(self.utils.getPathInvAlert('conf') + '/inv_alert_conf.yaml', 'r')['inv_folder']
		self.path_inventories = self.utils.getPathInvAlert(aux_folder_inv)

	"""
	Method that performs the configuration and creation of
	an inventory.

	Parameters:
	self -- An instantiated object of the Inventories class.
	"""
	def createInventory(self):
		data_inventory = []
		now = datetime.now()
		name_inventory = self.form_dialog.getDataInputText("Enter the inventory name:", "inv_name")
		data_inventory.append(name_inventory)
		frequency_inventory = self.form_dialog.getDataRadioList("Select a option:", self.options_frequency_inventory, "Inventory Frequency")
		data_inventory.append(frequency_inventory)
		time_execution = self.form_dialog.getDataTime("Choose the time it will run:", now.hour, now.minute)
		data_inventory.append(str(time_execution[0]) + ':' + str(time_execution[1]))
		index_name = self.form_dialog.getDataInputText("Enter the index pattern where the inventory will be obtained:", "audit-*")
		data_inventory.append(index_name)
		field_name = self.form_dialog.getDataInputText("Enter the name of the index field which stores to the hostname:", "info.host")
		data_inventory.append(field_name)
		telegram_bot_token = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram bot token:", "751988420:AAHrzn7RXWxVQQNha0tQUzyouE5lUcPde1g"))
		data_inventory.append(telegram_bot_token.decode('utf-8'))
		telegram_chat_id = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram channel identifier:", "-1002365478941"))
		data_inventory.append(telegram_chat_id.decode('utf-8'))
		self.createFileInventory(data_inventory)
		path_new_inventory = self.path_inventories + '/' + name_inventory
		if path.isdir(path_new_inventory) and path.exists(path_new_inventory + '/' + name_inventory + '.yaml'):
			self.utils.createInvAlertToolLog("Inventory created: " + name_inventory, 1)
			self.form_dialog.d.msgbox("\nInventory created: " + name_inventory + '.', 7, 50, title = "Notification Message")
		else:
			self.form_dialog.d.msgbox("\nFailed to create inventory. For more information, see the logs.", 8, 50, title = "Error Message") 
		self.form_dialog.mainMenu()

	"""
	Method that creates the directory and the configuration
	file of an inventory.

	Parameters:
	self -- An instantiated object of the Inventories class.
	data_inventory -- Variable that contains the information
	                  that will be stored in the configuration
	                  file corresponding to the inventory.
	"""
	def createFileInventory(self, data_inventory):
		data_json = {'name_inv' : data_inventory[0],
					'frequency_inv' : data_inventory[1],
					'time_execution' : data_inventory[2],
					'index_name' : data_inventory[3],
					'field_name' : data_inventory[4],
					'telegram_bot_token' : data_inventory[5],
					'telegram_chat_id' : data_inventory[6]}

		path_new_inventory = self.path_inventories + '/' + data_inventory[0]
		self.utils.createNewFolder(path_new_inventory)
		self.utils.createYamlFile(data_json, path_new_inventory + '/' + data_inventory[0] + '.yaml', 'w')

	"""
	Method that updates one or more fields of a specific
	inventory.

	Parameters:
	self -- An instantiated object of the Inventories class.
	"""
	def updateInventory(self):
		options_inv_fields = [("Name", "Inventory name", 0),
							("Frequency", "Frequency with which it is obtained", 0),
							("Time", "Time at which it is executed", 0),
							("Index", "Index name", 0),
							("Field", "Name of the field containing the hostname", 0),
							("Bot Token", "Telegram bot token", 0),
							("Chat ID", "Telegram channel identifier", 0)]
		
		list_inventories_aux = self.getListInventories()
		if len(list_inventories_aux) == 0:
			self.form_dialog.d.msgbox("\nNo inventories were found.", 7, 50, title = "Notification Message")
		else:
			flag_name = 0
			flag_frequency = 0
			flag_time = 0
			flag_index = 0
			flag_field = 0
			flag_bot_token = 0
			flag_chat_id = 0
			flag_rename = 0
			list_inventories = self.utils.convertListToCheckOrRadioList(list_inventories_aux)
			opt_list_inventories = self.form_dialog.getDataRadioList("Select a option:", list_inventories, "Inventories")
			path_inv_update = self.path_inventories + '/' + opt_list_inventories + '/' + opt_list_inventories + '.yaml'
			hash_data_inv = self.utils.getHashToFile(path_inv_update)
			data_inventory = self.utils.readYamlFile(path_inv_update, 'rU')
			opt_inv_fields = self.form_dialog.getDataCheckList("Select one or more options:", options_inv_fields, "Inventory Fields")
			for option in opt_inv_fields:
				if option == "Name":
					flag_name = 1
				elif option == "Frequency":
					flag_frequency = 1
				elif option == "Time":
					flag_time = 1
				elif option == "Index":
					flag_index = 1
				elif option == "Field":
					flag_field = 1
				elif option == "Bot Token":
					flag_bot_token = 1
				elif option == "Chat ID":
					flag_chat_id = 1
			try:
				previous_name = data_inventory['name_inv']
				if flag_name == 1:
					name_inventory = self.form_dialog.getDataInputText("Enter the inventory name:", data_inventory['name_inv'])
					if not data_inventory['name_inv'] == name_inventory:
						flag_rename = 1
						data_inventory['name_inv'] = name_inventory
				if flag_frequency == 1:
					for option in self.options_frequency_inventory:
						if option[0] == data_inventory['frequency_inv']:
							option[2] = 1
						else:
							option[2] = 0
					frequency_inventory = self.form_dialog.getDataRadioList("Select a option:", self.options_frequency_inventory, "Inventory Frequency")
					data_inventory['frequency_inv'] = frequency_inventory
				if flag_time == 1:
					aux_time = data_inventory['time_execution'].split(':')
					time_execution = self.form_dialog.getDataTime("Choose the time it will run:", aux_time[0], aux_time[1])
					data_inventory['time_execution'] = str(time_execution[0]) + ':' + str(time_execution[1])
				if flag_index == 1:
					index_name = self.form_dialog.getDataInputText("Enter the index pattern where the inventory will be obtained:", data_inventory['index_name'])
					data_inventory['index_name'] = index_name
				if flag_field == 1:
					field_name = self.form_dialog.getDataInputText("Enter the name of the index field which stores to the hostname:", data_inventory['field_name'])
					data_inventory['field_name'] = field_name
				if flag_bot_token == 1:
					telegram_bot_token = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram bot token:", self.utils.decryptAES(data_inventory['telegram_bot_token']).decode('utf-8')))
					data_inventory['telegram_bot_token'] = telegram_bot_token.decode('utf-8')
				if flag_chat_id == 1:
					telegram_chat_id = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the Telegram channel identifier:", self.utils.decryptAES(data_inventory['telegram_chat_id']).decode('utf-8')))
					data_inventory['telegram_chat_id'] = telegram_chat_id.decode('utf-8')
				self.utils.createYamlFile(data_inventory, path_inv_update, 'w')
				hash_data_inv_upd = self.utils.getHashToFile(path_inv_update)
				if hash_data_inv == hash_data_inv_upd:
					self.form_dialog.d.msgbox("\nInventory not updated.", 7, 50, title = "Notification Message")
				else:
					if flag_rename == 1:
						path_folder_update = self.path_inventories + '/' + previous_name
						rename(path_inv_update, path_folder_update + '/' + data_inventory['name_inv'] + '.yaml')
						rename(path_folder_update, self.path_inventories + '/' + data_inventory['name_inv'])
					self.form_dialog.d.msgbox("\nModified inventory: " + previous_name + '.', 7, 50, title = "Notification Message")
				self.form_dialog.mainMenu()
			except (OSError, KeyError) as exception:
				self.utils.createInvAlertToolLog(exception, 3)
				self.form_dialog.d.msgbox("\nFailed to update inventory. For more information, see the logs.", 8, 50, title = "Error Message")
				self.form_dialog.mainMenu()

	"""
	Method that eliminates one or more inventories.

	Parameters:
	self -- An instantiated object of the Inventories class.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def deleteInventory(self):
		list_inventories_aux = self.getListInventories()
		if len(list_inventories_aux) == 0:
			self.form_dialog.d.msgbox("\nNo inventories were found.", 7, 50, title = "Notification Message")
		else:
			try:
				list_inventories = self.utils.convertListToCheckOrRadioList(list_inventories_aux)
				opt_list_inventories = self.form_dialog.getDataCheckList("Select one or more options:", list_inventories, "Inventories")
				conf_to_delete = self.form_dialog.getDataYesOrNo("\nAre you sure to delete the selected inventories?", "Inventories")
				if conf_to_delete == "ok":
					message = "\nInventories removed:\n\n"
					for option in opt_list_inventories:
						path_inventory_to_delete = self.utils.getPathInvAlert(self.path_inventories) + '/' + option
						rmtree(path_inventory_to_delete)
						if not path.exists(path_inventory_to_delete):
							message += '- ' + option + '\n'
					self.form_dialog.getScrollBox(message, "Inventories removed")
				self.form_dialog.mainMenu()
			except OSError as exception:
				self.utils.createInvAlertToolLog(exception, 3)
				self.form_dialog.d.msgbox("\nError when deleting one or more inventories. For more information, see the logs.", 8, 50, title = "Error Message")
				self.form_dialog.mainMenu()

	"""
	Method that shows all the inventories created so far.

	Parameters:
	self -- An instantiated object of the Inventories class.
	"""
	def showAllInventories(self):
		list_inventories = self.getListInventories()
		if len(list_inventories) == 0:
			self.form_dialog.d.msgbox("\nNo inventories were found.", 7, 50, title = "Notification Message")
			self.form_dialog.mainMenu()
		else:
			message = "\nInventories in: " + self.path_inventories + '\n\n'
			message += "\n".join(list_inventories)
			self.form_dialog.getScrollBox(message, "Inventories")

	"""
	Method that obtains a list with all the inventories
	created.

	Parameters:
	self -- An instantiated object of the Inventories class.

	Return:
	sub_directories -- List with all inventories found.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def getListInventories(self):
		try:
			with scandir(self.path_inventories) as directories:
				sub_directories = [directory.name for directory in directories if directory.is_dir()]
		except OSError as exception:
			self.utils.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("\nError getting inventories. For more information, see the logs.", 8, 50, title = "Error Message")
			self.form_dialog.mainMenu()
		else:
			return sub_directories