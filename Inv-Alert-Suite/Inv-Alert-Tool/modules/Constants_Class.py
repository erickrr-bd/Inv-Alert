"""
Class that manages all the constant variables of the application.
"""
class Constants:
	"""
	Title that is shown in the background of the application.
	"""
	BACKTITLE = "INV-ALERT-TOOL"

	"""
	Absolute path of the VS-Monitor configuration file.
	"""
	PATH_FILE_CONFIGURATION = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/inv_alert_conf.yaml"

	"""
	Absolute path of the file where the key for the encryption/decryption process is stored.
	"""
	PATH_KEY_FILE = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/key"

	"""
	Absolute path of the application logs.
	"""
	NAME_FILE_LOG = "/var/log/Inv-Alert/inv-alert-tool-log-"

	"""
	Name of the application logs.
	"""
	NAME_LOG = "INV_ALERT_TOOL_LOG"

	"""
	Name of the user created for the operation of the application.
	"""
	USER = "inv_alert"

	"""
	Name of the group created for the operation of the application.
	"""
	GROUP = "inv_alert"

	"""
	Options displayed in the main menu.
	"""
	OPTIONS_MAIN_MENU = [("1", "Inv-Alert Configuration"),
						 ("2", "Inventories"),
				  	  	 ("3", "Inv-Alert Service"),
				  	  	 ("4", "About"),
			      	  	 ("5", "Exit")]

	"""
	Options that are shown when the configuration file does not exist.
	"""
	OPTIONS_CONFIGURATION_FALSE = [("Create", "Create the configuration file", 0)]

	"""
	Options that are shown when the configuration file exists.
	"""
	OPTIONS_CONFIGURATION_TRUE = [("Modify", "Modify the configuration file", 0)]