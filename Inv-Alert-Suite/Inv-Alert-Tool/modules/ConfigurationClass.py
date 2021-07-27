from os import path, rename
from modules.UtilsClass import Utils

"""
Class that manages everything related to the Inv-Alert
configuration.
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
		self.utils = Utils(form_dialog)
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
			data_conf.append(user_http_auth.decode('utf-8'))
			data_conf.append(pass_http_auth.decode('utf-8'))
		else:
			data_conf.append(False)
		self.createFileConfiguration(data_conf)
		if path.exists(self.conf_file):
			self.utils.createInvAlertToolLog("Configuration file created", 1)
			self.form_dialog.d.msgbox("\nConfiguration file created.", 7, 50, title = "Notification Message")
		else:
			self.form_dialog.d.msgbox("\nError creating configuration file. For more information, see the logs.", 8, 50, title = "Error Message")
		self.form_dialog.mainMenu()

	"""
	Method that modifies one or more values in the Inv-Alert
	configuration file.	

	Parameters:
	self -- An instantiated object of the Configuration class.

	Exceptions:
	KeyError -- A Python KeyError exception is what is raised
		   		when you try to access a key that isn’t in a 
		   		dictionary (dict). 
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def updateConfiguration(self):
		options_conf_fields = [("Version", "ElasticSearch Version", 0),
							("Host", "ElasticSearch Host", 0),
							("Port", "ElasticSearch Port", 0),
							("Folder Name", "Inventories Folder", 0),
							("SSL/TLS", "Enable or disable SSL/TLS connection", 0),
							("HTTP Authentication", "Enable or disable HTTP authentication", 0)]

		options_ssl_true = [("Disable", "Disable SSL/TLS communication", 0),
							("Certificate Validation", "Modify certificate validation", 0)]

		options_ssl_false = [("Enable", "Enable SSL/TLS communication", 0)]

		options_valid_cert_true = [("Disable", "Disable certificate validation", 0),
									("Certificate File", "Change certificate file", 0)]

		options_valid_cert_false = [("Enable", "Enable certificate validation", 0)]

		options_http_auth_true = [("Disable", "Disable HTTP authentication", 0),
								 ("Data", "Modify HTTP authentication data", 0)]

		options_http_auth_false = [("Enable", "Enable HTTP authentication", 0)]

		options_http_auth_data = [("Username", "Username for HTTP authentication", 0),
								 ("Password", "User password", 0)]

		flag_version = 0
		flag_es_host = 0
		flag_es_port = 0
		flag_folder_name = 0
		flag_use_ssl = 0
		flag_use_http_auth = 0
		flag_rename = 0
		opt_conf_fields = self.form_dialog.getDataCheckList("Select one or more options:", options_conf_fields, "Configuration File Fields")
		for option in opt_conf_fields:
			if option == "Version":
				flag_version = 1
			if option == "Host":
				flag_es_host = 1
			if option == "Port":
				flag_es_port = 1
			if option == "Folder Name":
				flag_folder_name = 1
			if option == "SSL/TLS":
				flag_use_ssl = 1
			if option == "HTTP Authentication":
				flag_use_http_auth = 1
		try:
			data_conf = self.utils.readYamlFile(self.conf_file, 'rU')
			hash_data_conf = self.utils.getHashToFile(self.conf_file)
			if flag_version == 1:
				version_es = self.form_dialog.getDataNumberDecimal("Enter the ElasticSearch version:", data_conf['es_version'])
				data_conf['es_version'] = version_es
			if flag_es_host == 1:
				host_es = self.form_dialog.getDataIP("Enter the ElasticSearch IP address:", data_conf['es_host'])
				data_conf['es_host'] = host_es
			if flag_es_port == 1:
				port_es = self.form_dialog.getDataPort("Enter the ElasticSearch listening port:", str(data_conf['es_port']))
				data_conf['es_port'] = int(port_es)
			if flag_folder_name == 1:
				folder_inv = self.form_dialog.getDataNameFolderOrFile("Enter the name of the folder where the inventories created will be saved:", data_conf['inv_folder'])
				if not data_conf['inv_folder'] == folder_inv:
					flag_rename = 1
					old_folder_inv = data_conf['inv_folder']
					data_conf['inv_folder'] = folder_inv
			if flag_use_ssl == 1:
				if data_conf['use_ssl'] == True:
					opt_ssl_true = self.form_dialog.getDataRadioList("Select a option:", options_ssl_true, "Connection SSL/TLS")
					if opt_ssl_true == "Disable":
						data_conf['use_ssl'] = False
						del data_conf['valid_certificate']
						if 'path_certificate' in data_conf:
							del data_conf['path_certificate']
					if opt_ssl_true == "Certificate Validation":
						if data_conf['valid_certificate'] == True:
							opt_valid_cert_true = self.form_dialog.getDataRadioList("Select a option:", options_valid_cert_true, "Certificate Validation")
							if opt_valid_cert_true == "Disable":
								data_conf['valid_certificate'] = False
								del data_conf['path_certificate']
							if opt_valid_cert_true == "Certificate File":
								cert_file = self.form_dialog.getFileOrDirectory(data_conf['path_certificate'], "Select the CA certificate:")
								data_conf['path_certificate'] = cert_file
						else:
							opt_valid_cert_false = self.form_dialog.getDataRadioList("Select a option:", options_valid_cert_false, "Certificate Validation")
							if opt_valid_cert_false == "Enable":
								data_conf['valid_certificate'] = True
								cert_file = self.form_dialog.getFileOrDirectory('/etc/Inv-Alert-Suite/Inv-Alert', "Select the CA certificate:")
								path_cert_json = { 'path_certificate' : cert_file }
								data_conf.update(path_cert_json)
				else:
					opt_ssl_false = self.form_dialog.getDataRadioList("Select a option:", options_ssl_false, "Connection SSL/TLS")
					if opt_ssl_false == "Enable":
						data_conf['use_ssl'] = True
						valid_certificate = self.form_dialog.getDataYesOrNo("\nDo you want the certificate for SSL/TLS communication to be validated?", "Certificate Validation")
						if valid_certificate == "ok":
							cert_file = self.form_dialog.getFileOrDirectory('/etc/Inv-Alert-Suite/Inv-Alert', "Select the CA certificate:")
							valid_cert_json = { 'valid_certificate' : True, 'path_certificate' : cert_file }
						else:
							valid_cert_json = { 'valid_certificate' : False}
						data_conf.update(valid_cert_json)
			if flag_use_http_auth == 1:
				if data_conf['use_http_auth'] == True:
					opt_http_auth_true = self.form_dialog.getDataRadioList("Select a option:", options_http_auth_true, "HTTP Authentication")
					if opt_http_auth_true == "Disable":
						data_conf['use_http_auth'] = False
						del data_conf['http_auth_user']
						del data_conf['http_auth_pass']
					elif opt_http_auth_true == "Data":
						flag_username = 0
						flag_password = 0
						opt_http_auth_data = self.form_dialog.getDataCheckList("Select one or more options:", options_http_auth_data, "HTTP Authentication")
						for option in opt_http_auth_data:
							if option == "Username":
								flag_username = 1
							elif option == "Password":
								flag_password = 1
						if flag_username == 1:
							user_http_auth = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the username for HTTP authentication:", "user_http"))
							data_conf['http_auth_user'] =  user_http_auth.decode('utf-8')
						if flag_password == 1:
							pass_http_auth = self.utils.encryptAES(self.form_dialog.getDataPassword("Enter the user's password for HTTP authentication:", "password"))
							data_conf['http_auth_pass'] = pass_http_auth.decode('utf-8')
				else:
					opt_http_auth_false = self.form_dialog.getDataRadioList("Select a option:", options_http_auth_false, "HTTP Authentication")
					if opt_http_auth_false == "Enable":
						data_conf['use_http_auth'] = True
						user_http_auth = self.utils.encryptAES(self.form_dialog.getDataInputText("Enter the username for HTTP authentication:", "user_http"))
						pass_http_auth = self.utils.encryptAES(self.form_dialog.getDataPassword("Enter the user's password for HTTP authentication:", "password"))
						http_auth_data_json = { 'http_auth_user' : user_http_auth.decode('utf-8'), 'http_auth_pass' : pass_http_auth.decode('utf-8') }
						data_conf.update(http_auth_data_json)
			self.utils.createYamlFile(data_conf, self.conf_file, 'w')
			hash_data_conf_upd = self.utils.getHashToFile(self.conf_file)
			if hash_data_conf == hash_data_conf_upd:
				self.form_dialog.d.msgbox("\nThe configuration file was not modified.", 7, 50, title = "Notification Message")
			else:
				if flag_rename == 1:
					rename(self.utils.getPathInvAlert(old_folder_inv), self.utils.getPathInvAlert(data_conf['inv_folder']))
				self.utils.createInvAlertToolLog("The configuration file was modified", 1)
				self.form_dialog.d.msgbox("\nThe configuration file was modified.", 7, 50, title = "Notification Message")
			self.form_dialog.mainMenu()
		except (OSError, KeyError) as exception:
			self.utils.createInvAlertToolLog(exception, 3)
			self.form_dialog.d.msgbox("Error modifying the configuration file. For more information, see the logs.", 8, 50, title = "Error Message")
			self.form_dialog.mainMenu()


	"""
	Method that creates the YAML file where the configuration
	is stored.

	Parameters:
	self -- An instantiated object of the Configuration class.
	data_conf -- Variable where all the information related to
				 the configuration is stored.
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
			http_auth_json = { 'use_http_auth' : data_conf[last_index + 1], 'http_auth_user' : data_conf[last_index + 2], 'http_auth_pass' : data_conf[last_index + 3] }
		else:
			http_auth_json = { 'use_http_auth' : data_conf[last_index + 1] }
		data_json.update(http_auth_json)

		inv_folder = self.utils.getPathInvAlert(data_conf[3])
		self.utils.createNewFolder(inv_folder)
		self.utils.createYamlFile(data_json, self.conf_file, 'w')