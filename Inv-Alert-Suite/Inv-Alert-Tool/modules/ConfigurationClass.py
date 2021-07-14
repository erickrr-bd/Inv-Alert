import os
import yaml
from modules.UtilsClass import Utils

"""
"""
class Configuration:
	"""
	Property that stores an object of type FormDialogs.
	"""
	form_dialog = None

	"""
	Property that stores the path of the configuration file.
	"""
	conf_file = None

	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Constructor for the Configuration class.

	Parameters:
	self -- An instantiated object of the Configuration class.
	"""
	def __init__(self, form_dialog):
		self.form_dialog = form_dialog
		self.utils = Utils(self.form_dialog)
		self.conf_file = self.utils.getPathInvAlert('conf') + '/inv_alert_conf.yaml'

	"""
	Method where all the necessary information for the
	configuration of Inv-Alert is defined.

	Parameters:
	self -- An instantiated object of the Configuration class.
	"""
	def createConfiguration(self):
		data_conf = []
		version_es = self.form_dialog.getDataNumberDecimal("Enter the ElasticSearch version:", "7.13")
		host_es = self.form_dialog.getDataIP("Enter the ElasticSearch IP address:", "localhost")
		port_es = self.form_dialog.getDataPort("Enter the ElasticSearch listening port:", "9200")
		folder_inv = self.form_dialog.getDataNameFolderOrFile("Enter the name of the folder where the inventories created will be saved:", "folder_inv")
		use_ssl = self.form_dialog.getDataYesOrNo("\nDo you want Inv-Alert to connect to ElasticSearch using the SSL/TLS protocol?", "Connection Via SSL/TLS")
		data_conf.append(version_es)
		data_conf.append(host_es)
		data_conf.append(port_es)
		data_conf.append(folder_inv)
		if use_ssl == "ok":
			data_conf.append(True)
			valid_certificate = self.form_dialog.getDataYesOrNo("\nDo you want the certificate for SSL/TLS communication to be validated?", "Certificate Validation")
			if valid_certificate == "ok":
				data_conf.append(True)
				cert_file = self.form_dialog.getFileOrDirectory('/etc/Inv-Alert-Suite/Inv-Alert', "Select the CA certificate:")
				data_conf.append(cert_file)
			else:
				data_conf.append(False)
		else:
			data_conf.append(False)
		http_auth = self.form_dialog.getDataYesOrNo("\nIs it required to enable the use of HTTP authentication to connect to ElasticSearch?", "HTTP Authentication")
		if http_auth == "ok":
			data_conf.append(True)
			user_http_auth = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the username for HTTP authentication:", "user_http"))
			pass_http_auth = self.utils.encryptAES(self.form_dialog.getDataPassword("Enter the user's password for HTTP authentication:", "password"))
			data_conf.append(user_http_auth)
			data_conf.append(pass_http_auth)
		else:
			data_conf.append(False)
		self.createFileConfiguration(data_conf)
		if os.path.exists(self.conf_file):
			self.utils.createInvAlertToolLog("Configuration file created", 2)
			self.form_dialog.d.msgbox("\nConfiguration file created", 7, 50, title = "Notification message")
		else:
			self.form_dialog.d.msgbox("\nError creating configuration file. For more information, see the logs.", 8, 50, title = "Error message")
		self.form_dialog.mainMenu()

	"""
	Method that creates the YAML file where the configuration
	is stored.

	Parameters:
	self -- An instantiated object of the Configuration class.
	data_conf -- Variable where all the information related to
				 the configuration is stored.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def createFileConfiguration(self, data_conf):
		data_json = {'es_version' : data_conf[0],
					'es_host' : data_conf[1],
					'es_port' : int(data_conf[2]),
					'inv_folder' : data_conf[3],
					'use_ssl' : data_conf[4]}
		
		if data_conf[4] == True:
			if data_conf[5] == True:
				valid_cert_json = { 'valid_certificate' : data_conf[5], 'path_certificate' : data_conf[6] }
				last_index = 6
			else:
				valid_cert_json = { 'valid_certificate' : data_conf[5] }
				last_index = 5
			data_json.update(valid_cert_json)
		else:
			last_index = 4

		if data_conf[last_index + 1] == True:
			http_auth_json = { 'use_http_auth' : data_conf[last_index + 1], 'http_auth_user' : data_conf[last_index + 2].decode("utf-8"), 'http_auth_pass' : data_conf[last_index + 3].decode("utf-8") }
		else:
			http_auth_json = { 'use_http_auth' : data_conf[last_index + 1] }
		data_json.update(http_auth_json)
		try:
			inv_folder = self.utils.getPathInvAlert(data_conf[3])
			if(not os.path.isdir(inv_folder)):
				os.mkdir(inv_folder)
				self.utils.ownerChange(inv_folder)
			with open(self.conf_file, 'w') as config_file:
				yaml.dump(data_json, config_file, default_flow_style = False)
			self.utils.ownerChange(self.conf_file)
		except OSError as exception:
			self.utils.createInvAlertToolLog(exception, 4)