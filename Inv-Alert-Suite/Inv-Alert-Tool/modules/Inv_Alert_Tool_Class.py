"""
Class that manages everything related to Inv-Alert-Tool.
"""
from os import path
from sys import exit
from libPyLog import libPyLog
from dataclasses import dataclass
from libPyUtils import libPyUtils
from libPyDialog import libPyDialog
from .Constants_Class import Constants
from .Inventories_Class import Inventories
from libPyConfiguration import libPyConfiguration

@dataclass
class InvAlertTool:

	def __init__(self) -> None:
		"""
		Class constructor.
		"""
		self.logger = libPyLog()
		self.utils = libPyUtils()
		self.constants = Constants()
		self.dialog = libPyDialog(self.constants.BACKTITLE)


	def main_menu(self) -> None:
		"""
		Main menu.
    	"""
		try:
			option = self.dialog.create_menu("Select a option:", 12, 50, self.constants.MAIN_MENU_OPTIONS, "Main Menu")
			self.switch_main_menu(int(option))
		except KeyboardInterrupt:
			pass


	def inventories_menu(self) -> None:
		"""
		Inventories' menu.
		"""
		option = self.dialog.create_menu("Select a option:", 13, 50, self.constants.INVENTORIES_MENU_OPTIONS, "Inventories Menu")
		self.switch_inventories_menu(int(option))


	def disable_enable_inventories_menu(self) -> None:
		"""
		Disable/Enable Inventories menu.
		"""
		option = self.dialog.create_menu("Select a option:", 9, 50, self.constants.DISABLE_ENABLE_MENU_OPTIONS, "Disable/Enable Inventories Menu")
		self.switch_disable_enable_inventories_menu(int(option))


	def service_menu(self) -> None:
		"""
		Inv-Alert's service menu.
		"""
		option = self.dialog.create_menu("Select a option:", 11, 50, self.constants.SERVICE_MENU_OPTIONS, "Inv-Alert Service Menu")
		self.switch_service_menu(int(option))


	def switch_main_menu(self, option: int) -> None:
		"""
		Method that executes an action based on the option chosen in the "Main" menu.

		Parameters:
    		option (int): Chosen option.
		"""
		match option:
			case 1:
				self.define_configuration()
			case 2:
				self.inventories_menu()
			case 3:
				self.service_menu()
			case 4:
				self.display_about()
			case 5:
				exit(1)


	def switch_inventories_menu(self, option: int) -> None:
		"""
		Method that executes an action based on the option chosen in the "Inventories" menu.

		Parameters:
    		option (int): Chosen option.
		"""
		inventory = Inventories()
		match option:
			case 1:
				self.create_inventory()
			case 2:
				inventory.modify_inventory()
			case 3:
				inventory.display_configuration()
			case 4:
				inventory.delete_inventories()
			case 5:
				self.disable_enable_inventories_menu()
			case 6:
				inventory.display_inventories()


	def switch_disable_enable_inventories_menu(self, option: int) -> None:
		"""
		Method that executes an action based on the option chosen in the "Disable/Enable Inventories" menu.

		Parameters:
    		option (int): Chosen option.
		"""
		inventory = Inventories()
		match option:
			case 1:
				inventory.disable_inventory()
			case 2:
				inventory.enable_inventory()


	def switch_service_menu(self, option: int) -> None:
		"""
		Method that executes an action based on the option chosen in the "Inv-Alert Service" menu.

		Parameters:
    		option (int): Chosen option.
		"""
		match option:
			case 1:
				result = self.utils.manage_daemon("inv-alert.service", 1)
				if result == 0:
					self.dialog.create_message("\nInv-Alert service started.", 7, 50, "Notification Message")
					self.logger.create_log("Inv-Alert service started", 2, "_manageService", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 2:
				result = self.utils.manage_daemon("inv-alert.service", 2)
				if result == 0:
					self.dialog.create_message("\nInv-Alert service restarted.", 7, 50, "Notification Message")
					self.logger.create_log("Inv-Alert service restarted", 2, "_manageService", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 3:
				result = self.utils.manage_daemon("inv-alert.service", 3)
				if result == 0:
					self.dialog.create_message("\nInv-Alert service stopped.", 7, 50, "Notification Message")
					self.logger.create_log("Inv-Alert service stopped", 3, "_manageService", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 4:
				service_status = self.utils.get_detailed_status_by_daemon("inv-alert.service", "/tmp/inv_alert.status")
				self.dialog.create_scrollbox(service_status, 18, 70, "Inv-Alert Service")


	def define_configuration(self) -> None:
		"""
		Method that defines the action to be performed on the Inv-Alert's configuration.
		"""
		if not path.exists(self.constants.INV_ALERT_CONFIGURATION):
			option = self.dialog.create_radiolist("Select a option:", 8, 50, self.constants.CONFIGURATION_OPTIONS_FALSE, "Inv-Alert Configuration")
			if option == "Create":
				self.create_configuration()
		else:
			option = self.dialog.create_radiolist("Select a option:", 9, 50, self.constants.CONFIGURATION_OPTIONS_TRUE, "Inv-Alert Configuration")
			self.modify_configuration() if option == "Modify" else self.display_configuration()


	def create_configuration(self) -> None:
		"""
		Method that creates the Inv-Alert's configuration.
		"""
		inv_alert_data = libPyConfiguration(self.constants.BACKTITLE)
		inv_alert_data.define_es_host()
		inv_alert_data.define_verificate_certificate()
		inv_alert_data.define_use_authentication(self.constants.KEY_FILE)
		inv_alert_data.create_file(inv_alert_data.convert_object_to_dict(), self.constants.INV_ALERT_CONFIGURATION, self.constants.LOG_FILE, self.constants.USER, self.constants.GROUP)


	def modify_configuration(self) -> None:
		"""
		Method that updates or modifies the Inv-Alert's configuration.
		"""
		inv_alert_data = libPyConfiguration(self.constants.BACKTITLE)
		inv_alert_data.modify_configuration(self.constants.INV_ALERT_CONFIGURATION, self.constants.KEY_FILE, self.constants.LOG_FILE, self.constants.USER, self.constants.GROUP)


	def display_configuration(self) -> None:
		"""
		Method that displays the Inv-Alert's configuration.
		"""
		inv_alert_data = libPyConfiguration(self.constants.BACKTITLE)
		inv_alert_data.display_configuration(self.constants.INV_ALERT_CONFIGURATION, self.constants.LOG_FILE, self.constants.USER, self.constants.GROUP)


	def create_inventory(self) -> None:
		"""
		Method that creates the Inventory's configuration.
		"""
		inv_alert_data = Inventories()
		inv_alert_data.define_name()
		inv_alert_data.define_execution_time()
		inv_alert_data.define_index_pattern()
		inv_alert_data.define_timestamp_field()
		inv_alert_data.define_hostname_field()
		inv_alert_data.define_ip_address_field()
		inv_alert_data.define_telegram_bot_token()
		inv_alert_data.define_telegram_chat_id()
		inv_alert_data.create_file(inv_alert_data.convert_object_to_dict())


	def display_about(self) -> None:
		"""
		Method that displays the about of the application.
		"""
		try:
			text = "\nAuthor: Erick Roberto Rodríguez Rodríguez\nEmail: erickrr.tbd93@gmail.com, erodriguez@tekium.mx\nGithub: https://github.com/erickrr-bd/Inv-Alert\nInv-Alert v3.3 - November 2025" + "\n\nPython tool for automating the daily inventory of assets\nregistered in a specific index pattern."
			self.dialog.create_scrollbox(text, 13, 60, "About")
		except KeyboardInterrupt:
			pass
		finally:
			raise KeyboardInterrupt("Error")
