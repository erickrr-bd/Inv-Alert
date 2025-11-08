"""
Class that manages the application's constants.
"""
from dataclasses import dataclass

@dataclass(frozen = True)
class Constants:
	"""
	Inv-Alert's configuration file.
	"""
	INV_ALERT_CONFIGURATION: str = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/inv_alert.yaml"

	"""
	Inventories' path.
	"""
	INVENTORIES_FOLDER: str = "/etc/Inv-Alert-Suite/Inv-Alert/inventories"

	"""
	Encryption key's path.
	"""
	KEY_FILE: str = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/key"

	"""
	Inv-Alert's log file.
	"""
	LOG_FILE: str = "/var/log/Inv-Alert/inv-alert-log"

	"""
	Owner user.
	"""
	USER: str = "inv_alert"

	"""
	Owner group.
	"""
	GROUP: str = "inv_alert"
