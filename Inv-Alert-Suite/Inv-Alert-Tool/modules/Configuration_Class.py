from os import path
from libPyLog import libPyLog
from libPyUtils import libPyUtils
from libPyDialog import libPyDialog
from .Constants_Class import Constants

"""
Class that manages what is related to the configuration of Inv-Alert.
"""
class Configuration:
	"""
	Attribute that stores an object of the libPyUtils class.
	"""
	__utils = None

	"""
	Attribute that stores an object of the libPyDialog class.
	"""
	__dialog = None

	"""
	Attribute that stores an object of the libPyLog class.
	"""
	__logger = None

	"""
	Attribute that stores an object of the Constants class.
	"""
	__constants = None

	"""
	Attribute that stores the method to be called when the user chooses the cancel option.
	"""
	__action_to_cancel = None
	

	def __init__(self, action_to_cancel):
		"""
		Method that corresponds to the constructor of the class.

		:arg action_to_cancel (object): Method to be called when the user chooses the cancel option.
		"""
		self.__logger = libPyLog()
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__action_to_cancel = action_to_cancel
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, action_to_cancel)

	
	def createConfiguration(self):
		"""
		Method that collects the information for the creation of the Inv-Alert configuration file.
		"""
		data_configuration = []
		try:
			es_host = self.__dialog.createInputBoxToIPDialog("Enter the ElasticSearch IP address:", 8, 50, "localhost")
			data_configuration.append(es_host)
			es_port = self.__dialog.createInputBoxToPortDialog("Enter the ElasticSearch listening port:", 8, 50, "9200")
			data_configuration.append(es_port)
			use_ssl_tls = self.__dialog.createYesOrNoDialog("\nDo you require Inv-Alert to communicate with ElasticSearch using the SSL/TLS protocol?", 8, 50, "SSL/TLS Connection")
			if use_ssl_tls == "ok":
				data_configuration.append(True)
				validate_certificate_ssl = self.__dialog.createYesOrNoDialog("\nDo you require Inv-Alert to validate the SSL certificate?", 8, 50, "Certificate Validation")
				if validate_certificate_ssl == "ok":
					data_configuration.append(True)
					path_certificate_file = self.__dialog.createFileDialog("/etc/Inv-Alert-Suite/Inv-Alert", 8, 50, "Select the CA certificate:", ".pem")
					data_configuration.append(path_certificate_file)
				else:
					data_configuration.append(False)
			else:
				data_configuration.append(False)
			use_http_authentication = self.__dialog.createYesOrNoDialog("\nIs the use of HTTP authentication required to connect to ElasticSearch?", 8, 50, "HTTP Authentication")
			if use_http_authentication == "ok":
				passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
				data_configuration.append(True)
				user_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the username for HTTP authentication:", 8, 50, "user_http"), passphrase)
				data_configuration.append(user_http_authentication.decode("utf-8"))
				password_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createPasswordBoxDialog("Enter the user's password for HTTP authentication:", 8, 50, "password", True), passphrase)
				data_configuration.append(password_http_authentication.decode("utf-8"))
			else:
				data_configuration.append(False)
			self.__createYamlFileConfiguration(data_configuration)
			if path.exists(self.__constants.PATH_FILE_CONFIGURATION):
				self.__dialog.createMessageDialog("\nConfiguration file created.", 7, 50, "Notification Message")
				self.__logger.generateApplicationLog("Configuration file created", 1, "__createConfigurationInvAlert", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except (OSError, IOError, FileNotFoundError) as exception:
			self.__dialog.createMessageDialog("\nError to create the configuration file. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__createConfigurationInvAlert", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def modifyConfiguration(self):
		"""
		Method that allows to modify one or more values in the Inv-Alert configuration file.
		"""
		options_fields_update = self.__dialog.createCheckListDialog("Select one or more options:", 12, 70, self.__constants.OPTIONS_FIELDS_UPDATE, "Configuration Fields")
		try:
			data_configuration = self.__utils.readYamlFile(self.__constants.PATH_FILE_CONFIGURATION)
			hash_file_configuration_original = self.__utils.getHashFunctionToFile(self.__constants.PATH_FILE_CONFIGURATION)
			if "Host" in options_fields_update:
				es_host = self.__dialog.createInputBoxToIPDialog("Enter the ElasticSearch IP address:", 8, 50, data_configuration["es_host"])
				data_configuration["es_host"] = es_host
			if "Port" in options_fields_update:
				es_port = self.__dialog.createInputBoxToPortDialog("Enter the ElasticSearch listening port:", 8, 50, str(data_configuration["es_port"]))
				data_configuration["es_port"] = int(es_port)
			if "SSL/TLS" in options_fields_update:
				if data_configuration["use_ssl_tls"] == True:
					option_ssl_tls_true = self.__dialog.createRadioListDialog("Select a option:", 10, 70, self.__constants.OPTIONS_SSL_TLS_TRUE, "SSL/TLS Connection")
					if option_ssl_tls_true == "Disable":
						del data_configuration["validate_certificate_ssl"]
						if "path_certificate_file" in data_configuration:
							del data_configuration["path_certificate_file"]
						data_configuration["use_ssl_tls"] = False
					elif option_ssl_tls_true == "Certificate Validation":
						if data_configuration["validate_certificate_ssl"] == True:
							option_validate_certificate_true = self.__dialog.createRadioListDialog("Select a option:", 10, 70, self.__constants.OPTIONS_VALIDATE_CERTIFICATE_TRUE, "Certificate Validation")
							if option_validate_certificate_true == "Disable":
								if "path_certificate_file" in data_configuration:
									del data_configuration["path_certificate_file"]
								data_configuration["validate_certificate_ssl"] = False
							elif data_configuration["validate_certificate_ssl"] == "Certificate File":
								path_certificate_file = self.__dialog.createFileDialog(data_configuration["path_certificate_file"], 8, 50, "Select the CA certificate:", ".pem")
								data_configuration["path_certificate_file"] = path_certificate_file
						else:
							option_validate_certificate_false = self.__dialog.createRadioListDialog("Select a option:", 8, 70, self.__constants.OPTIONS_VALIDATE_CERTIFICATE_FALSE, "Certificate Validation")
							if option_validate_certificate_false == "Enable":
								data_configuration["validate_certificate_ssl"] = True
								path_certificate_file = self.__dialog.createFileDialog("/etc/Inv-Alert-Suite/Inv-Alert", 8, 50, "Select the CA certificate:", ".pem")
								validate_certificate_ssl_json = {"path_certificate_file" : path_certificate_file}
								data_configuration.update(validate_certificate_ssl_json)
				else:
					option_ssl_tls_false = self.__dialog.createRadioListDialog("Select a option:", 8, 70, self.__constants.OPTIONS_SSL_TLS_FALSE, "SSL/TLS Connection")
					data_configuration["use_ssl_tls"] = True
					validate_certificate_ssl = self.__dialog.createYesOrNoDialog("\nDo you require VS-Monitor to validate the SSL certificate?", 8, 50, "Certificate Validation")
					if validate_certificate_ssl == "ok":
						path_certificate_file = self.__dialog.createFileDialog("/etc/Inv-Alert-Suite/Inv-Alert", 8, 50, "Select the CA certificate:", ".pem")
						validate_certificate_ssl_json = {"validate_certificate_ssl" : True, "path_certificate_file" : path_certificate_file}
					else:
						validate_certificate_ssl_json = {"validate_certificate_ssl" : False}
					data_configuration.update(validate_certificate_ssl_json)
			if "HTTP Authentication" in options_fields_update:
				if data_configuration["use_http_authentication"] == True:
					option_http_authentication_true = self.__dialog.createRadioListDialog("Select a option:", 10, 70, self.__constants.OPTIONS_HTTP_AUTHENTICATION_TRUE, "HTTP Authentication")
					if option_http_authentication_true == "Disable":
						del data_configuration["user_http_authentication"]
						del data_configuration["password_http_authentication"]
						data_configuration["use_http_authentication"] = False
					elif option_http_authentication_true == "Data":
						passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
						options_http_authentication_data = self.__dialog.createCheckListDialog("Select one or more options:", 10, 70, self.__constants.OPTIONS_HTTP_AUTHENTICATION_DATA, "HTTP Authentication")
						if "Username" in options_http_authentication_data:
							user_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the username for HTTP authentication:", 8, 50, "user_http"), passphrase)
							data_configuration["user_http_authentication"] = user_http_authentication.decode("utf-8")
						if "Password" in options_http_authentication_data:
							password_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createPasswordBoxDialog("Enter the user's password for HTTP authentication:", 8, 50, "password", True), passphrase)
							data_configuration["password_http_authentication"] = password_http_authentication.decode("utf-8")
				else:
					option_http_authentication_false = self.__dialog.createRadioListDialog("Select a option:", 8, 70, self.__constants.OPTIONS_HTTP_AUTHENTICATION_FALSE, "HTTP Authentication")
					if option_http_authentication_false == "Enable":
						passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
						user_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the username for HTTP authentication:", 8, 50, "user_http"), passphrase)
						password_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createPasswordBoxDialog("Enter the user's password for HTTP authentication:", 8, 50, "password", True), passphrase)
						http_authentication_json = {"user_http_authentication" : user_http_authentication.decode("utf-8"), "password_http_authentication" : password_http_authentication.decode("utf-8")}
						data_configuration.update(http_authentication_json)
						data_configuration["use_http_authentication"] = True
			self.__utils.createYamlFile(data_configuration, self.__constants.PATH_FILE_CONFIGURATION)
			hash_file_configuration_new = self.__utils.getHashFunctionToFile(self.__constants.PATH_FILE_CONFIGURATION)
			if hash_file_configuration_new == hash_file_configuration_original:
				self.__dialog.createMessageDialog("\nConfiguration file not modified.", 7, 50, "Notification Message")
			else:
				self.__dialog.createMessageDialog("\nConfiguration file modified.", 7, 50, "Notification Message")
				self.__logger.generateApplicationLog("Configuration file modified", 2, "__modifyConfigurationInvAlert", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except KeyError as exception:
			self.__dialog.createMessageDialog("\nKey Error: " + str(exception) + ".", 7, 50, "Error Message")
			self.__logger.generateApplicationLog("Key Error: " + str(exception), 3, "__modifyConfigurationInvAlert", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()
		except (IOError, FileNotFoundError, OSError) as exception:
			self.__dialog.createMessageDialog("\nError reading or modifying the configuration file. For more information, see the logs.", 8, 50, "Error Message")
			self.__logger.generateApplicationLog(exception, 3, "__modifyConfigurationInvAlert", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			self.__action_to_cancel()


	def __createYamlFileConfiguration(self, data_configuration):
		"""
		Method that creates the YAML file corresponding to the Inv-Alert configuration.

		:arg data_configuration (list): Data to be stored in the configuration file.
		"""
		data_configuration_json = {"es_host" : data_configuration[0],
								   "es_port" : data_configuration[1],
								   "use_ssl_tls" : data_configuration[2]}

		if data_configuration[2] == True:
			if data_configuration[3] == True:
				validate_certificate_ssl_json = {"validate_certificate_ssl" : data_configuration[3], "path_certificate_file" : data_configuration[4]}
				last_index = 4
			else:
				validate_certificate_ssl_json = {"validate_certificate_ssl" : data_configuration[3]}
				last_index = 3
			data_configuration_json.update(validate_certificate_ssl_json)
		else:
			last_index = 2
		if data_configuration[last_index + 1] == True:
			http_authentication_json = {"use_http_authentication" : data_configuration[last_index + 1], "user_http_authentication" : data_configuration[last_index + 2], "password_http_authentication" : data_configuration[last_index + 3]}
			last_index += 3
		else:
			http_authentication_json = {"use_http_authentication" : data_configuration[last_index + 1]}
			last_index += 1
		data_configuration_json.update(http_authentication_json)

		self.__utils.createYamlFile(data_configuration_json, self.__constants.PATH_FILE_CONFIGURATION)
		self.__utils.changeOwnerToPath(self.__constants.PATH_FILE_CONFIGURATION, self.__constants.USER, self.__constants.GROUP)