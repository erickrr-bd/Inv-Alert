from os import path
from sys import exit
from .Service_Class import Service
from libPyDialog import libPyDialog
from .Constants_Class import Constants
from .Inventories_Class import Inventories
from .Configuration_Class import Configuration

"""
Class that manages what is related to the interfaces and actions of Inv-Alert-Tool.
"""
class InvAlertTool:
	"""
	Attribute that stores an object of the libPyDialog class.
	"""
	__dialog = None

	"""
	Attribute that stores an object of the Constants class.
	"""
	__constants = None


	def __init__(self):
		"""
		Method that corresponds to the constructor of the class.
		"""
		self.__constants = Constants()
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, self.mainMenu)
		

	def mainMenu(self):
		"""
		Method that shows the main menu of the application.
		"""
		option_main_menu = self.__dialog.createMenuDialog("Select a option:", 14, 50, self.__constants.OPTIONS_MAIN_MENU, "Main Menu")
		self.__switchMainMenu(int(option_main_menu))


	def __inventoriesMenu(self):
		"""
		Method that shows the Inventories menu.
		"""
		option_inventories_menu = self.__dialog.createMenuDialog("Select a option:", 12, 50, self.__constants.OPTIONS_INVENTORIES, "Inventories Menu")
		self.__switchInventoriesMenu(int(option_inventories_menu))


	def __serviceMenu(self):
		"""
		Method that shows the Service menu.
		"""
		option_service_menu = self.__dialog.createMenuDialog("Select a option:", 12, 50, self.__constants.OPTIONS_SERVICE_MENU, "Service Menu")
		self.__switchServiceMenu(int(option_service_menu))


	def __switchMainMenu(self, option):
		"""
		Method that executes a certain action based on the number of the option chosen in the Main menu.

		:arg option: Option number.
		"""
		if option == 1:
			self.__defineConfiguration()
		elif option == 2:
			self.__inventoriesMenu()
		elif option == 3:
			self.__serviceMenu()
		elif option == 4:
			print("Hola")
		elif option == 5:
			exit(1)


	def __switchInventoriesMenu(self, option):
		"""
		Method that executes a certain action based on the number of the option chosen in the Inventories menu.

		:arg option: Option number.
		"""
		inventories = Inventories(self.mainMenu)
		if option == 1:
			inventories.createNewInventory()
		elif option == 2:
			inventories.updateInventory()
		elif option == 3:
			inventories.deleteInventories()
		elif option == 4:
			inventories.showAllInventories()


	def __switchServiceMenu(self, option):
		"""
		Method that executes a certain action based on the number of the option chosen in the Service menu.

		:arg option: Option number.
		"""
		service = Service(self.mainMenu)
		if option == 1:
			service.startService()
		elif option == 2:
			service.restartService()
		elif option == 3:
			service.stopService()
		elif option == 4:
			service.getActualStatusService()


	def __defineConfiguration(self):
		"""
		Method that defines the action to perform on the Inv-Alert configuration (create or modify).
		"""
		configuration = Configuration(self.mainMenu)
		if not path.exists(self.__constants.PATH_FILE_CONFIGURATION):
			option_configuration_false = self.__dialog.createRadioListDialog("Select a option:", 8, 50, self.__constants.OPTIONS_CONFIGURATION_FALSE, "Configuration Options")
			if option_configuration_false == "Create":
				configuration.createConfiguration()
		else:
			option_configuration_true = self.__dialog.createRadioListDialog("Select a option:", 8, 50, self.__constants.OPTIONS_CONFIGURATION_TRUE, "Configuration Options")
			if option_configuration_true == "Modify":
				configuration.modifyConfiguration()