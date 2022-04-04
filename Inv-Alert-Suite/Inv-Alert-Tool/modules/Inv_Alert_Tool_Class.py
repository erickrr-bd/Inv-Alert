from sys import exit
from libPyDialog import libPyDialog
from .Constants_Class import Constants

class InvAlertTool:

	__dialog = None

	__constants = None

	def __init__(self):
		self.__constants = Constants()
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, self.mainMenu)
		

	def mainMenu(self):
		"""
		Method that shows the main menu of the application.
		"""
		option_main_menu = self.__dialog.createMenuDialog("Select a option:", 14, 50, self.__constants.OPTIONS_MAIN_MENU, "Main Menu")
		self.__switchMainMenu(int(option_main_menu))


	def __switchMainMenu(self, option):
		"""
		Method that executes a certain action based on the number of the option chosen in the Main menu.

		:arg option: Option number.
		"""
		if option == 1:
			print("Hola")
		elif option == 2:
			print("Hola")
		elif option == 3:
			print("Hola")
		elif option == 4:
			print("Hola")
		elif option == 5:
			exit(1)