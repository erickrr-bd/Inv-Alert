"""
Class that manages the application's constants.
"""
from typing import List
from dataclasses import dataclass, field

@dataclass(frozen = True)
class Constants:
	"""
	Message displayed in the background.
	"""
	BACKTITLE: str = "INV-ALERT-TOOL v3.3 by Erick Rodriguez"

	"""
	Inv-Alert's configuration file.
	"""
	INV_ALERT_CONFIGURATION: str = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/inv_alert.yaml"

	"""
	Inventories' path.
	"""
	INVENTORIES_FOLDER: str = "/etc/Inv-Alert-Suite/Inv-Alert/inventories"

	"""
	Encryption key's file.
	"""
	KEY_FILE: str = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/key"

	"""
	Inv-Alert-Tool's log file.
	"""
	LOG_FILE: str = "/var/log/Inv-Alert/inv-alert-tool-log"

	"""
	Owner user.
	"""
	USER: str = "inv_alert"

	"""
	Owner group.
	"""
	GROUP: str = "inv_alert"

	"""
	Options displayed in the "Main" menu.
	"""
	MAIN_MENU_OPTIONS: List = field(default_factory = lambda : [("1", "Configuration"), ("2", "Inventories"), ("3", "Service"), ("4", "About"), ("5", "Exit")])

	"""
	Options that are displayed when the configuration file doesn't exist.
	"""
	CONFIGURATION_OPTIONS_FALSE: List = field(default_factory = lambda : [("Create", "Create the configuration file", 0)])

	"""
	Options that are displayed when the configuration file exists.
	"""
	CONFIGURATION_OPTIONS_TRUE: List = field(default_factory = lambda : [("Modify", "Modify the configuration file", 0), ("Display", "Display the configuration file", 0)])
	
	"""
	Options displayed in the "Inventories" menu.
	"""
	INVENTORIES_MENU_OPTIONS: List = field(default_factory = lambda : [("1", "Create inventory"), ("2", "Modify inventory"), ("3", "Display inventory's configuration"), ("4", "Delete inventory(s)"), ("5", "Disable/Enable inventory(s)"), ("6", "Display inventory(s)")])

	"""
	Options displayed in the "Service" menu.
	"""
	SERVICE_MENU_OPTIONS: List = field(default_factory = lambda : [("1", "Start Service"), ("2", "Restart Service"), ("3", "Stop Service"), ("4", "Service Status")])

	"""
	Inventory's fields.
	"""
	INVENTORY_FIELDS: List = field(default_factory = lambda : [("Name", "Inventory's name", 0), ("Time", "Execution Time", 0), ("Index", "ElasticSearch's index pattern", 0), ("Timestamp", "Timestamp field's name", 0), ("Hostname", "Hostname field's name", 0), ("IP", "IP Address field's name", 0), ("Bot Token", "Telegram Bot Token", 0), ("Chat ID", "Telegram channel identifier", 0)])

	"""
	Options displayed in the "Disable/Enable Inventories" menu.
	"""
	DISABLE_ENABLE_MENU_OPTIONS: List = field(default_factory = lambda : [("1", "Disable Inventories"), ("2", "Enable Inventories")])
