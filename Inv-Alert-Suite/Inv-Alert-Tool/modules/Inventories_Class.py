from os import path
from libPyLog import libPyLog
from libPyUtils import libPyUtils
from libPyDialog import libPyDialog
from .Constants_Class import Constants

"""
Class that manages everything related to inventories.
"""
class Inventories:
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

		:arg action_to_cancel (object): Method to be called when the user chooses the cancel option.
		"""
		self.__logger = libPyLog()
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__action_to_cancel = action_to_cancel
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, action_to_cancel)


	def createNewInventory(self):
		"""
		Method that creates a new inventory.
		"""
		data_inventory = []
		try:
			inventory_name = self.__dialog.createFolderOrFileNameDialog("Enter inventory name:", 8, 50, "inventory_one")
			data_inventory.append(inventory_name)
			inventory_time_execution = self.__dialog.createTimeDialog("Choose the time:", 4, 10, -1, -1)
			data_inventory.append(str(inventory_time_execution[0]) + ':' + str(inventory_time_execution[1]))
			index_pattern_name = self.__dialog.createInputBoxDialog("Enter the index pattern:", 8, 50, "winlogbeat-*")
			data_inventory.append(index_pattern_name)
			field_name_in_index = self.__dialog.createInputBoxDialog("Enter the name of the index field that corresponds to the hostname:", 10, 50, "host.hostname")
			data_inventory.append(field_name_in_index)
			passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
			telegram_bot_token = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram bot token:", 8, 50, "751988420:AAHrzn7RXWxVQQNha0tQUzyouE5lUcPde1g"), passphrase)
			data_inventory.append(telegram_bot_token.decode("utf-8"))
			telegram_chat_id = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram channel identifier:", 8, 50, "-1002365478941"), passphrase)
			data_inventory.append(telegram_chat_id.decode("utf-8"))
			path_new_inventory = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory[0]
			path_new_inventory_yaml = path_new_inventory + '/' + data_inventory[0] + ".yaml"
			self.__createInventoryFileYaml(data_inventory, path_new_inventory, path_new_inventory_yaml)
			if path.exists(path_new_inventory_yaml):
				self.__dialog.createMessageDialog("\nInventory created: " + inventory_name + '.', 7, 50, "Notification Message")
				self.__logger.generateApplicationLog("Inventory created: " + inventory_name, 1, "__createNewInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except (FileNotFoundError, OSError, IOError) as exception:
			self.__dialog.createMessageDialog("\nError to create new inventory. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__createNewInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def updateInventory(self):
		"""
		Method that updates one or more values of an inventory.
		"""
		try:
			list_all_inventories = self.__utils.getListToAllSubDirectories(self.__constants.PATH_INVENTORIES_FOLDER)
			if not list_all_inventories:
				self.__dialog.createMessageDialog("\nNo inventories found.", 7, 50, "Notification Message")
			else:
				flag_rename_inventory = 0
				list_dialog_inventories = self.__utils.convertListToDialogList(list_all_inventories, "Inventory Name")
				option_list_inventories = self.__dialog.createRadioListDialog("Select a option:", 12, 50, list_dialog_inventories, "Inventories")
				path_inventory_to_update = self.__constants.PATH_INVENTORIES_FOLDER + '/' + option_list_inventories + '/' + option_list_inventories + ".yaml"
				data_inventory = self.__utils.readYamlFile(path_inventory_to_update)
				hash_inventory_file_yaml_old = self.__utils.getHashFunctionToFile(path_inventory_to_update)
				options_fields_update = self.__dialog.createCheckListDialog("Select one or more options:", 14, 70, self.__constants.OPTIONS_FIELDS_UPDATE_INVENTORIES, "Inventory Fields")
				inventory_name_actual = data_inventory["inventory_name"]
				if "Name" in options_fields_update:
					inventory_name = self.__dialog.createFolderOrFileNameDialog("Enter inventory name:", 8, 50, data_inventory["inventory_name"])
					if not inventory_name == data_inventory["inventory_name"]:
						flag_rename_inventory = 1
						data_inventory["inventory_name"] = inventory_name
				if "Time" in options_fields_update:
					inventory_time_execution_actual = data_inventory["inventory_time_execution"].split(':')
					inventory_time_execution = self.__dialog.createTimeDialog("Choose the time:", 4, 10, int(inventory_time_execution_actual[0]), int(inventory_time_execution_actual[1]))
					data_inventory["inventory_time_execution"] = str(inventory_time_execution[0]) + ':' + str(inventory_time_execution[1])
				if "Index" in options_fields_update:
					index_pattern_name = self.__dialog.createInputBoxDialog("Enter the index pattern:", 8, 50, data_inventory["index_pattern_name"])
					data_inventory["index_pattern_name"] = index_pattern_name
				if "Field" in options_fields_update:
					field_name_in_index = self.__dialog.createInputBoxDialog("Enter the name of the index field that corresponds to the hostname:", 10, 50, data_inventory["field_name_in_index"])
					data_inventory["field_name_in_index"] = field_name_in_index
				if "Bot Token" in options_fields_update:
					passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
					telegram_bot_token = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram bot token:", 8, 50, self.__utils.decryptDataWithAES(data_inventory["telegram_bot_token"], passphrase).decode("utf-8")), passphrase)
					data_inventory["telegram_bot_token"] = telegram_bot_token.decode("utf-8")
				if "Chat ID" in options_fields_update:
					passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
					telegram_chat_id = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram channel identifier:", 8, 50, self.__utils.decryptDataWithAES(data_inventory["telegram_chat_id"], passphrase).decode("utf-8")), passphrase)
					data_inventory["telegram_chat_id"] = telegram_chat_id.decode("utf-8")
				self.__utils.createYamlFile(data_inventory, path_inventory_to_update)
				hash_inventory_file_yaml_new = self.__utils.getHashFunctionToFile(path_inventory_to_update)
				if hash_inventory_file_yaml_old == hash_inventory_file_yaml_new:
					self.__dialog.createMessageDialog("\nNo changes were made to inventory.", 7, 50, "Notification Message")
				else:
					if flag_rename_inventory == 1:
						path_inventory_actual = self.__constants.PATH_INVENTORIES_FOLDER + '/' + inventory_name_actual
						self.__utils.renameFileOrFolder(path_inventory_to_update, path_inventory_actual + '/' + inventory_name + ".yaml")
						self.__utils.renameFileOrFolder(path_inventory_actual, self.__constants.PATH_INVENTORIES_FOLDER + '/' + inventory_name)
					self.__dialog.createMessageDialog("\nModified inventory: " + inventory_name_actual + '.', 7, 50, "Notification Message")
					self.__logger.generateApplicationLog("Modified inventory: " + inventory_name_actual, 2, "__modifyInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except KeyError as exception:
			self.__dialog.createMessageDialog("\nKey Error: " + str(exception), 7, 50, "Error Message")
			self.__logger.generateApplicationLog("Key Error: " + str(exception), 3, "__modifyInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except (OSError, IOError, FileNotFoundError) as exception:
			self.__dialog.createMessageDialog("\nError to open, read or modify a file or directory. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__modifyInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def deleteInventories(self):
		"""
		Method that eliminates one or more inventories.
		"""
		try:
			list_all_inventories = self.__utils.getListToAllSubDirectories(self.__constants.PATH_INVENTORIES_FOLDER)
			if not list_all_inventories:
				self.__dialog.createMessageDialog("\nNo inventories found.", 7, 50, "Notification Message")
			else:
				list_dialog_inventories = self.__utils.convertListToDialogList(list_all_inventories, "Inventory Name")
				option_list_inventories = self.__dialog.createCheckListDialog("Select a option:", 12, 50, list_dialog_inventories, "Inventories")
				confirmation_to_delete = self.__dialog.createYesOrNoDialog("\nDo you want to delete the selected inventories?\n\n**This action cannot be reversed.", 10, 50, "Delete Inventories")
				if confirmation_to_delete == "ok":
					message_to_show = "\nDeleted Inventories:\n\n"
					for inventory in option_list_inventories:
						path_inventory_to_delete = self.__constants.PATH_INVENTORIES_FOLDER + '/' + inventory
						self.__utils.deleteFolder(path_inventory_to_delete)
						if not path.exists(path_inventory_to_delete):
							message_to_show += "- " + inventory + '\n'
							self.__logger.generateApplicationLog("Deleted Inventory: " + inventory, 2, "__deleteInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
					self.__dialog.createScrollBoxDialog(message_to_show, 16, 50, "Delete Inventories")
			self.__action_to_cancel()
		except OSError as exception:
			self.__dialog.createMessageDialog("\nError to delete the inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__deleteInventory", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def showAllInventories(self):
		"""
		Method that shows all inventories created so far.
		"""
		try:
			list_all_inventories = self.__utils.getListToAllSubDirectories(self.__constants.PATH_INVENTORIES_FOLDER)
			if not list_all_inventories:
				self.__dialog.createMessageDialog("\nNo inventories found.", 7, 50, "Notification Message")
			else:
				message_to_show = "\nInventories:\n\n"
				message_to_show += "- "+ "\n- ".join(list_all_inventories)
				self.__dialog.createScrollBoxDialog(message_to_show, 16, 50, "Inventories")
			self.__action_to_cancel()
		except OSError as exception:
			self.__dialog.createMessageDialog("\nError to get inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__showInventories", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def __createInventoryFileYaml(self, data_inventory, path_new_inventory, path_new_inventory_yaml):
		"""
		Method that creates the YAML file corresponding to the new inventory.

		:arg data_inventory (list): Data to be stored in the inventory file.
		:arg path_new_inventory (string): Absolute path of the directory corresponding to the new inventory.
		:arg path_new_inventory_yaml (string): Absolute path of the YAML file corresponding to the new inventory.
		"""
		data_inventory_json = {"inventory_name" : data_inventory[0],
							   "inventory_time_execution" : data_inventory[1],
							   "index_pattern_name" : data_inventory[2],
							   "field_name_in_index" : data_inventory[3],
							   "telegram_bot_token" : data_inventory[4],
							   "telegram_chat_id" : data_inventory[5]}
		
		self.__utils.createNewFolder(path_new_inventory)
		self.__utils.changeOwnerToPath(path_new_inventory, self.__constants.USER, self.__constants.GROUP)
		self.__utils.createYamlFile(data_inventory_json, path_new_inventory_yaml)
		self.__utils.changeOwnerToPath(path_new_inventory_yaml, self.__constants.USER, self.__constants.GROUP)