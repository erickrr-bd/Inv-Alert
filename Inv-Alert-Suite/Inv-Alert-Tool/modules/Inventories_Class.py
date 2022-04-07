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
	Attribute that stores the passphrase for encryption/decryption process.
	"""
	__passphrase = None

	"""
	Attribute that stores the method to be called when the user chooses the cancel option.
	"""
	__action_to_cancel = None


	def __init__(self, action_to_cancel):
		"""
		Method that corresponds to the constructor of the class.
		"""
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__action_to_cancel = action_to_cancel
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, action_to_cancel)
		self.__passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
		self.__logger = libPyLog(self.__constants.NAME_FILE_LOG, self.__constants.NAME_LOG, self.__constants.USER, self.__constants.GROUP)


	def createNewInventory(self):
		"""
		Method that creates a new inventory.
		"""
		data_inventory = []
		inventory_name = self.__dialog.createFolderOrFileNameDialog("Enter inventory name:", 8, 50, "inventory_one")
		data_inventory.append(inventory_name)
		inventory_time_execution = self.__dialog.createTimeDialog("Choose the time:", 4, 10, -1, -1)
		data_inventory.append(str(inventory_time_execution[0]) + ':' + str(inventory_time_execution[1]))
		index_pattern_name = self.__dialog.createInputBoxDialog("Enter the index pattern:", 8, 50, "winlogbeat-*")
		data_inventory.append(index_pattern_name)
		field_name_in_index = self.__dialog.createInputBoxDialog("Enter the name of the index field that corresponds to the hostname:", 10, 50, "host.hostname")
		data_inventory.append(field_name_in_index)
		telegram_bot_token = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram bot token:", 8, 50, "751988420:AAHrzn7RXWxVQQNha0tQUzyouE5lUcPde1g"), self.__passphrase)
		data_inventory.append(telegram_bot_token.decode('utf-8'))
		telegram_chat_id = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the Telegram channel identifier:", 8, 50, "-1002365478941"), self.__passphrase)
		data_inventory.append(telegram_chat_id.decode('utf-8'))
		path_new_inventory = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory[0]
		path_new_inventory_yaml = path_new_inventory + '/' + data_inventory[0] + ".yaml"
		self.__createInventoryFileYaml(data_inventory, path_new_inventory, path_new_inventory_yaml)
		if path.exists(path_new_inventory_yaml):
			self.__logger.createApplicationLog("Configuration file created", 1)
			self.__dialog.createMessageDialog("\nConfiguration file created.", 7, 50, "Notification Message")
		self.__action_to_cancel()


	def __createInventoryFileYaml(self, data_inventory, path_new_inventory, path_new_inventory_yaml):
		"""
		Method that creates the YAML file corresponding to the new inventory.

		:arg data_configuration: Data to be stored in the inventory file.
		:arg path_new_inventory: Absolute path of the directory corresponding to the new inventory.
		:arg path_new_inventory_yaml: Absolute path of the YAML file corresponding to the new inventory.
		"""
		data_inventory_json = {'inventory_name' : data_inventory[0],
					'inventory_time_execution' : data_inventory[1],
					'index_pattern_name' : data_inventory[2],
					'field_name_in_index' : data_inventory[3],
					'telegram_bot_token' : data_inventory[4],
					'telegram_chat_id' : data_inventory[5]}
		try:
			self.__utils.createNewFolder(path_new_inventory)
			self.__utils.changeOwnerToPath(path_new_inventory, self.__constants.USER, self.__constants.GROUP)
			self.__utils.createYamlFile(data_inventory_json, path_new_inventory_yaml)
			self.__utils.changeOwnerToPath(path_new_inventory_yaml, self.__constants.USER, self.__constants.GROUP)
		except (OSError, IOError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__dialog.createMessageDialog("\nError creating YAML file. For more information, see the logs.", 8, 50, "Error Message")
			self.__action_to_cancel()