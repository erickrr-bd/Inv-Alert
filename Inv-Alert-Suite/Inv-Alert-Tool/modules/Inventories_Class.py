"""
Class that manages everything related to Inventories.
"""
from os import path
from json import dumps
from libPyLog import libPyLog
from libPyUtils import libPyUtils
from libPyDialog import libPyDialog
from .Constants_Class import Constants
from dataclasses import dataclass, field

@dataclass
class Inventories:

	name: str = None
	execution_time: str = None
	index_pattern: str = None
	timestamp_field: str = None
	hostname_field: str = None
	ip_address_field: str = None
	telegram_bot_token: tuple = field(default_factory = tuple)
	telegram_chat_id: tuple = field(default_factory = tuple)


	def __init__(self) -> None:
		"""
		Class constructor.
		"""
		self.logger = libPyLog()
		self.utils = libPyUtils()
		self.constants = Constants()
		self.dialog = libPyDialog(self.constants.BACKTITLE)


	def define_name(self) -> None:
		"""
		Method that defines the inventory's name.
		"""
		self.name = self.dialog.create_filename_inputbox("Enter the inventory's name:", 8, 50, "windows_inventory")


	def define_execution_time(self) -> None:
		"""
		Method that defines the time at which the inventory will be executed.
		"""
		selected_time = self.dialog.create_time("Select the time:", 2, 50, -1, -1)
		self.execution_time = f"{selected_time[0]}:{selected_time[1]}"


	def define_index_pattern(self) -> None:
		"""
		Method that defines the inventory's index pattern.
		"""
		self.index_pattern = self.dialog.create_inputbox("Enter the index pattern:", 8, 50, "winlogbeat-*")


	def define_timestamp_field(self) -> None:
		"""
		Method that defines the field's name corresponding to the index timestamp.
		"""
		self.timestamp_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the index timestamp:", 9, 50, "@timestamp")


	def define_hostname_field(self) -> None:
		"""
		Method that defines the field's name corresponding to the hostname.
		"""
		self.hostname_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the hostname:", 9, 50, "host.hostname")


	def define_ip_address_field(self) -> None:
		"""
		Method that defines the field's name corresponding to the IP Address.
		"""
		self.ip_address_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the IP Address:", 9, 50, "host.ip")


	def define_telegram_bot_token(self) -> None:
		"""
		Method that defines the Telegram Bot Token.
		"""
		passphrase = self.utils.get_passphrase(self.constants.KEY_FILE)
		self.telegram_bot_token = self.utils.encrypt_data(self.dialog.create_inputbox("Enter the Telegram Bot Token:", 8, 50, "751988420:AAHrzn7RXWxVQQNha0tQUzyouE5lUcPde1g"), passphrase)


	def define_telegram_chat_id(self) -> None:
		"""
		Method that defines the Telegram Chat ID.
		"""
		passphrase = self.utils.get_passphrase(self.constants.KEY_FILE)
		self.telegram_chat_id = self.utils.encrypt_data(self.dialog.create_inputbox("Enter the Telegram Chat ID:", 8, 50, "-1002365478941"), passphrase)


	def convert_object_to_dict(self) -> dict:
		"""
		Method that converts an Inventories's object into a dictionary.

		Returns:
			inventory_data_json (dict): Dictionary with the object's data.
		"""
		inventory_data_json = {
			"name" :  self.name,
			"execution_time" :  self.execution_time,
			"index_pattern" : self.index_pattern,
			"timestamp_field" : self.timestamp_field,
			"hostname_field" : self.hostname_field,
			"ip_address_field" : self.ip_address_field,
			"telegram_bot_token" : self.telegram_bot_token,
			"telegram_chat_id" : self.telegram_chat_id
		}
		return inventory_data_json


	def convert_dict_to_object(self, inventory_data: dict) -> None:
		"""
		Method that converts a dictionary into an Inventories' object.

		Parameters:
			inventory_data (dict): Object that contains the inventory's configuration data.
		"""
		self.name = inventory_data["name"]
		self.execution_time = inventory_data["execution_time"]
		self.index_pattern = inventory_data["index_pattern"]
		self.timestamp_field = inventory_data["timestamp_field"]
		self.hostname_field = inventory_data["hostname_field"]
		self.ip_address_field = inventory_data["ip_address_field"]
		self.telegram_bot_token  = inventory_data["telegram_bot_token"]
		self.telegram_chat_id = inventory_data["telegram_chat_id"]


	def create_file(self, inventory_data: dict) -> None:
		"""
		Method that creates the YAML file corresponding to the inventory.

		Parameters:
			inventory_data (dict): Object that contains the inventory's configuration data.
		"""
		try:
			inventory_path = f"{self.constants.INVENTORIES_FOLDER}/{inventory_data["name"]}"
			self.utils.create_folder(inventory_path)
			self.utils.change_owner(inventory_path, self.constants.USER, self.constants.GROUP, "750")
			inventory_file = f"{self.constants.INVENTORIES_FOLDER}/{inventory_data["name"]}/{inventory_data["name"]}.yaml"
			self.utils.create_yaml_file(inventory_data, inventory_file)
			self.utils.change_owner(inventory_file, self.constants.USER, self.constants.GROUP, "640")
			if path.exists(inventory_file):
				self.dialog.create_message(f"\nInventory created: {inventory_data["name"]}", 7, 50, "Notification Message")
				self.logger.create_log(f"Inventory created: {inventory_data["name"]}", 2, "__createInventory", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except Exception as exception:
			self.dialog.create_message("\nError creating inventory. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "__createInventory", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def modify_inventory(self) -> None:
		"""
		Method that modifies the inventory's configuration.
		"""
		try:
			inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				tuple_to_rc = self.utils.convert_list_to_tuple_rc(inventories, "Inventory's Name")
				option = self.dialog.create_radiolist("Select a option:", 18, 70, tuple_to_rc, "Inventories")
				inventory_data = self.utils.read_yaml_file(f"{self.constants.INVENTORIES_FOLDER}/{option}/{option}.yaml")
				original_hash = self.utils.get_hash_from_file(f"{self.constants.INVENTORIES_FOLDER}/{option}/{option}.yaml")
				options = self.dialog.create_checklist("Select one or more options:", 15, 70, self.constants.INVENTORY_FIELDS, "Inventory's Fields")
				self.convert_dict_to_object(inventory_data)
				if "Name" in options:
					self.modify_name()
				if "Time" in options:
					self.modify_execution_time()
				if "Index" in options:
					self.modify_index_pattern()
				if "Timestamp" in options:
					self.modify_timestamp_field()
				if "Hostname" in options:
					self.modify_hostname_field()
				if "IP" in options:
					self.modify_ip_address_field()
				if "Bot Token" in options:
					self.modify_telegram_bot_token()
				if "Chat ID" in options:
					self.modify_telegram_chat_id()
				inventory_data = self.convert_object_to_dict()
				self.utils.create_yaml_file(inventory_data, f"{self.constants.INVENTORIES_FOLDER}/{self.name}/{self.name}.yaml")
				new_hash = self.utils.get_hash_from_file(f"{self.constants.INVENTORIES_FOLDER}/{self.name}/{self.name}.yaml")
				self.dialog.create_message("\nInventory not modified.", 7, 50, "Notification Message") if new_hash == original_hash else self.dialog.create_message("\nInventory modified.", 7, 50, "Notification Message")
			else:
				self.dialog.create_message(f"\nNo inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError modifying inventory's configuration. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_modifyInventory", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def modify_name(self) -> None:
		"""
		Method that modifies the inventory's name.
		"""
		old_name = self.name
		new_name = self.dialog.create_filename_inputbox("Enter the inventory's name:", 8, 50, old_name)
		if new_name == old_name:
			self.dialog.create_message("\nThe name cannot be the same as the previous one.", 8, 50, "Notification Message")
		else:
			self.utils.rename_file_or_folder(f"{self.constants.INVENTORIES_FOLDER}/{old_name}", f"{self.constants.INVENTORIES_FOLDER}/{new_name}")
			self.utils.rename_file_or_folder(f"{self.constants.INVENTORIES_FOLDER}/{new_name}/{old_name}.yaml", f"{self.constants.INVENTORIES_FOLDER}/{new_name}/{new_name}.yaml")
			self.name = new_name
			self.logger.create_log(f"Inventory's name modified: {new_name}", 3, f"_{old_name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_execution_time(self) -> None:
		"""
		Method that modifies the time at which the inventory will be executed.
		"""
		old_execution_time = self.execution_time.split(':')
		selected_time = self.dialog.create_time("Select the time:", 2, 50, int(old_execution_time[0]), int(old_execution_time[1]))
		self.execution_time = f"{selected_time[0]}:{selected_time[1]}"
		self.logger.create_log(f"Execution Time modified: {self.execution_time}", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_index_pattern(self) -> None:
		"""
		Method that modifies the inventory's index pattern.
		"""
		self.index_pattern = self.dialog.create_inputbox("Enter the index pattern:", 8, 50, self.index_pattern)
		self.logger.create_log(f"Index pattern modified: {self.index_pattern}", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_timestamp_field(self) -> None:
		"""
		Method that modifies the field's name corresponding to the index timestamp.
		"""
		self.timestamp_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the index timestamp:", 9, 50, self.timestamp_field)
		self.logger.create_log(f"Timestamp field's name modified: {self.timestamp_field}", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_hostname_field(self) -> None:
		"""
		Method that modifies the field's name corresponding to the hostname.
		"""
		self.hostname_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the hostname:", 9, 50, self.hostname_field)
		self.logger.create_log(f"Hostname field's name modified: {self.hostname_field}", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_ip_address_field(self) -> None:
		"""
		Method that modifies the field's name corresponding to the IP Address.
		"""
		self.ip_address_field = self.dialog.create_inputbox("Enter the field's name that corresponds to the IP Address:", 9, 50, self.ip_address_field)
		self.logger.create_log(f"IP Address field's name modified: {self.ip_address_field}", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_telegram_bot_token(self) -> None:
		"""
		Method that modifies the Telegram Bot Token.
		"""
		passphrase = self.utils.get_passphrase(self.constants.KEY_FILE)
		self.telegram_bot_token = self.utils.encrypt_data(self.dialog.create_inputbox("Enter the Telegram Bot Token:", 8, 50, self.utils.decrypt_data(self.telegram_bot_token, passphrase).decode("utf-8")), passphrase)
		self.logger.create_log("Telegram Bot Token modified.", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def modify_telegram_chat_id(self) -> None:
		"""
		Method that modifies the Telegram Chat ID.
		"""
		passphrase = self.utils.get_passphrase(self.constants.KEY_FILE)
		self.telegram_chat_id = self.utils.encrypt_data(self.dialog.create_inputbox("Enter the Telegram Chat ID:", 8, 50, self.utils.decrypt_data(self.telegram_chat_id, passphrase).decode("utf-8")), passphrase)
		self.logger.create_log("Telegram Chat ID modified.", 3, f"_{self.name}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def display_configuration(self) -> None:
		"""
		Method that displays the inventory's configuration.
		"""
		try:
			inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				tuple_to_rc = self.utils.convert_list_to_tuple_rc(inventories, "Inventory's name")
				option = self.dialog.create_radiolist("Select a option:", 18, 70, tuple_to_rc, "Inventories")
				inventory_str = self.utils.convert_yaml_to_str(f"{self.constants.INVENTORIES_FOLDER}/{option}/{option}.yaml")
				text = f"\n{option}\n\n{inventory_str}"
				self.dialog.create_scrollbox(text, 18, 70, "Inventory's Configuration") 
			else:
				self.dialog.create_message(f"\nNo inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError displaying inventory's configuration. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_displayInventoryConf", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def delete_inventories(self) -> None:
		"""
		Method that deletes one or more inventories.
		"""
		try:
			inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				tuple_to_rc = self.utils.convert_list_to_tuple_rc(inventories, "Inventory's name")
				options = self.dialog.create_checklist("Select one or more options:", 18, 70, tuple_to_rc, "Delete Inventories")
				text = self.utils.get_str_from_list(options, "Inventories selected to remove:")
				self.dialog.create_scrollbox(text, 14, 50, "Delete Inventories")
				delete_inventories_yn = self.dialog.create_yes_or_no("\nAre you sure to delete the selected inventories?\n\n**Note: This action cannot be undone.", 10, 50, "Delete Inventories")
				if delete_inventories_yn == "ok":
					[self.utils.delete_folder(f"{self.constants.INVENTORIES_FOLDER}/{inventory}") for inventory in options]
					self.dialog.create_message("\nInventories deleted.", 7, 50, "Notification Message")
					self.logger.create_log(f"Inventories deleted: {','.join(options)}", 3, "_deleteInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			else:
				self.dialog.create_message(f"\nNo inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError deleting inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_deleteInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def disable_inventory(self)-> None:
		"""
		Method that disables one or more inventories.
		"""
		try:
			inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				tuple_to_rc = self.utils.convert_list_to_tuple_rc(inventories, "Inventory's name")
				options = self.dialog.create_checklist("Select one or more options:", 18, 70, tuple_to_rc, "Disable Inventories")
				text = self.utils.get_str_from_list(options, "Inventories selected to disable:")
				self.dialog.create_scrollbox(text, 14, 50, "Disable Inventories")
				disable_inventories_yn = self.dialog.create_yes_or_no("\nAre you sure to disable the selected inventories?", 8, 50, "Disable Inventories")
				if disable_inventories_yn == "ok":
					[self.utils.rename_file_or_folder(f"{self.constants.INVENTORIES_FOLDER}/{inventory}", f"{self.constants.INVENTORIES_FOLDER}/{inventory}.disabled") for inventory in options]
					self.dialog.create_message("\nInventories disabled.", 7, 50, "Notification Message")
					self.logger.create_log(f"Inventories disabled: {','.join(options)}", 3, "_disableInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			else:
				self.dialog.create_message(f"\nNo inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError disabling inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_disableInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def enable_inventory(self)-> None:
		"""
		Method that enables one or more inventories.
		"""
		try:
			inventories = self.utils.get_disabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				tuple_to_rc = self.utils.convert_list_to_tuple_rc(inventories, "Inventory's name")
				options = self.dialog.create_checklist("Select one or more options:", 18, 70, tuple_to_rc, "Enable Inventories")
				text = self.utils.get_str_from_list(options, "Inventories selected to enable:")
				self.dialog.create_scrollbox(text, 14, 50, "Enable Inventories")
				enable_inventories_yn = self.dialog.create_yes_or_no("\nAre you sure to enable the selected inventories?", 8, 50, "Enable Inventories")
				if enable_inventories_yn == "ok":
					[self.utils.rename_file_or_folder(f"{self.constants.INVENTORIES_FOLDER}/{inventory}", f"{self.constants.INVENTORIES_FOLDER}/{inventory[:-9]}") for inventory in options]
					self.dialog.create_message("\nInventories enabled.", 7, 50, "Notification Message")
					self.logger.create_log(f"Inventories enabled: {','.join(options)}", 3, "_enableInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			else:
				self.dialog.create_message(f"\nNo disabled inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError enabling inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_enableInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")


	def display_inventories(self) -> None:
		"""
		Method that displays all inventories.
		"""
		try:
			inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
			if inventories:
				inventories.sort()
				text = "\nInventories\n"
				for inventory in inventories:
					text += "\n- " + inventory
				self.dialog.create_scrollbox(text, 18, 70, "Inventories")
			else:
				self.dialog.create_message(f"\nNo inventories in: {self.constants.INVENTORIES_FOLDER}", 8, 50, "Notification Message")
		except Exception as exception:
			self.dialog.create_message("\nError displaying inventories. For more information, see the logs.", 8, 50, "Error Message")
			self.logger.create_log(exception, 4, "_displayInventories", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Exit")
