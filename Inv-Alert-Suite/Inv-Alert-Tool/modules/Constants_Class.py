"""
Class that manages all the constant variables of the application.
"""
class Constants:
	"""
	Title that is shown in the background of the application.
	"""
	BACKTITLE = "INV-ALERT-TOOL"

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
	NAME_FILE_LOG = "/var/log/Inv-Alert/inv-alert-tool-log-"

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

	"""
	Options that are shown when a value is going to be modified in the Inv-Alert configuration.
	"""
	OPTIONS_FIELDS_UPDATE = [("Host", "ElasticSearch Host", 0),
							 ("Port", "ElasticSearch Port", 0),
							 ("SSL/TLS", "Enable or disable SSL/TLS connection", 0),
							 ("HTTP Authentication", "Enable or disable Http authentication", 0)]

	"""
	Options displayed when the use of SSL/TLS is enabled.
	"""
	OPTIONS_SSL_TLS_TRUE = [("Disable", "Disable SSL/TLS communication", 0),
							("Certificate Validation", "Modify certificate validation", 0)]

	"""
	Options displayed when the use of SSL/TLS is disabled.
	"""
	OPTIONS_SSL_TLS_FALSE = [("Enable", "Enable SSL/TLS communication", 0)]

	"""
	Options displayed when SSL certificate validation is enabled.
	"""
	OPTIONS_VALIDATE_CERTIFICATE_TRUE = [("Disable", "Disable certificate validation", 0),
								   		 ("Certificate File", "Change certificate file", 0)]

	"""
	Options displayed when SSL certificate validation is disabled.
	"""
	OPTIONS_VALIDATE_CERTIFICATE_FALSE = [("Enable", "Enable certificate validation", 0)]

	"""
	Options that are displayed when HTTP authentication is enabled.
	"""
	OPTIONS_HTTP_AUTHENTICATION_TRUE = [("Disable", "Disable HTTP Authentication", 0),
								 		("Data", "Modify HTTP Authentication data", 0)]

	"""
	Options that are displayed when HTTP authentication is disabled.
	"""
	OPTIONS_HTTP_AUTHENTICATION_FALSE = [("Enable", "Enable HTTP Authentication", 0)]

	"""
	Options that are displayed when the HTTP authentication credentials are to be modified.
	"""
	OPTIONS_HTTP_AUTHENTICATION_DATA = [("Username", "Username for HTTP Authentication", 0),
								 		("Password", "User password", 0)]

	"""
	Options displayed in the Inventories menu.
	"""
	OPTIONS_INVENTORIES = [("1", "Create Inventory"),
					  	   ("2", "Update Inventory"),
					  	   ("3", "Delete Inventories"),
					  	   ("4", "Show all Inventories")]

	"""
	Options that are shown when a value is going to be modified in an inventory.
	"""
	OPTIONS_FIELDS_UPDATE_INVENTORIES = [("Name", "Inventory name", 0),
										 ("Time", "Time at which it is executed", 0),
										 ("Index", "Index pattern name", 0),
										 ("Field", "Name of the field containing the hostname", 0),
										 ("Bot Token", "Telegram bot token", 0),
								  		 ("Chat ID", "Telegram channel identifier", 0)]

	"""
	Options displayed in the service menu.
	"""
	OPTIONS_SERVICE_MENU = [("1", "Start Service"),
				            ("2", "Restart Service"),
				            ("3", "Stop Service"),
				            ("4", "Service Status")]