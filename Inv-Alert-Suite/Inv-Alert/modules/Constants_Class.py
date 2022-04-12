"""
Class that manages all the constant variables of the application.
"""
class Constants:
	"""
	Absolute path of the Inv-Alert configuration file.
	"""
	PATH_FILE_CONFIGURATION = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/inv_alert_conf.yaml"

	"""
	Absolute path of the file where the key for the encryption/decryption process is stored.
	"""
	PATH_KEY_FILE = "/etc/Inv-Alert-Suite/Inv-Alert/configuration/key"

	"""
	Absolute path of the VS-Monitor configuration file.
	"""
	PATH_INVENTORIES_FOLDER = "/etc/Inv-Alert-Suite/Inv-Alert/inventories"

	"""
	Absolute path of the application logs.
	"""
	NAME_FILE_LOG = "/var/log/Inv-Alert/inv-alert-log-"

	"""
	Name of the application logs.
	"""
	NAME_LOG = "INV_ALERT_LOG"

	"""
	Name of the user created for the operation of the application.
	"""
	USER = "inv_alert"

	"""
	Name of the group created for the operation of the application.
	"""
	GROUP = "inv_alert"