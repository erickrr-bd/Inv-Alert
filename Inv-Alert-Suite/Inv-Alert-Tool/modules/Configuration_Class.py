from os import path
from libPyLog import libPyLog
from libPyUtils import libPyUtils
from libPyDialog import libPyDialog
from .Constants_Class import Constants

class Configuration:

	__utils = None

	__dialog = None

	__constants = None

	__passphrase = None

	__action_to_cancel = None
	

	def __init__(self, action_to_cancel):
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__action_to_cancel = action_to_cancel
		self.__dialog = libPyDialog(self.__constants.BACKTITLE, action_to_cancel)
		self.__passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
		self.__logger = libPyLog(self.__constants.NAME_FILE_LOG, self.__constants.NAME_LOG, self.__constants.USER, self.__constants.GROUP)

	
	def createConfiguration(self):
		"""
		Method that collects the information for the creation of the Inv-Alert configuration file.
		"""
		data_configuration = []
		try:
			es_version = self.__dialog.createInputBoxToDecimalDialog("Enter the ElasticSearch version:", 8, 50, "7.17")
			data_configuration.append(es_version)
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
					path_certificate_file = self.__dialog.createFileDialog("/etc", 8, 50, "Select the CA certificate:", ".pem")
					data_configuration.append(path_certificate_file)
				else:
					data_configuration.append(False)
			else:
				data_configuration.append(False)
			use_http_authentication = self.__dialog.createYesOrNoDialog("\nIs the use of HTTP authentication required to connect to ElasticSearch?", 8, 50, "HTTP Authentication")
			if use_http_authentication == "ok":
				data_configuration.append(True)
				user_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createInputBoxDialog("Enter the username for HTTP authentication:", 8, 50, "user_http"), self.__passphrase)
				data_configuration.append(user_http_authentication.decode('utf-8'))
				password_http_authentication = self.__utils.encryptDataWithAES(self.__dialog.createPasswordBoxDialog("Enter the user's password for HTTP authentication:", 8, 50, "password", True), self.__passphrase)
				data_configuration.append(password_http_authentication.decode('utf-8'))
			else:
				data_configuration.append(False)
			self.__createFileYamlConfiguration(data_configuration)
			if path.exists(self.__constants.PATH_FILE_CONFIGURATION):
				self.__logger.createApplicationLog("Configuration file created", 1)
				self.__dialog.createMessageDialog("\nConfiguration file created.", 7, 50, "Notification Message")
			else:
				self.__dialog.createMessageDialog("\nError creating configuration file. For more information, see the logs.", 8, 50, "Error Message")
			self.__action_to_cancel()
		except FileNotFoundError as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__dialog.createMessageDialog("\nAn error has occurred. For more information, see the logs.", 8, 50, "Error Message")
			self.__action_to_cancel()


	def __createFileYamlConfiguration(self, data_configuration):
		"""
		Method that creates the YAML file corresponding to the VS-Monitor configuration.

		:arg data_configuration: Data to be stored in the configuration file.
		"""
		data_configuration_json = {'es_version' : data_configuration[0],
								   'es_host' : data_configuration[1],
								   'es_port' : data_configuration[2],
								   'use_ssl_tls' : data_configuration[3]}

		if data_configuration[3] == True:
			if data_configuration[4] == True:
				validate_certificate_ssl_json = {'validate_certificate_ssl' : data_configuration[4],
												 'path_certificate_file' : data_configuration[5]}
				last_index = 5
			else:
				validate_certificate_ssl_json = {'validate_certificate_ssl' : data_configuration[4]}
				last_index = 4
			data_configuration_json.update(validate_certificate_ssl_json)
		else:
			last_index = 3
		if data_configuration[last_index + 1] == True:
			http_authentication_json = {'use_http_authentication' : data_configuration[last_index + 1],
										'user_http_authentication' : data_configuration[last_index + 2],
										'password_http_authentication' : data_configuration[last_index + 3]}
			last_index += 3
		else:
			http_authentication_json = {'use_http_authentication' : data_configuration[last_index + 1]}
			last_index += 1
		data_configuration_json.update(http_authentication_json)
		try:
			self.__utils.createYamlFile(data_configuration_json, self.__constants.PATH_FILE_CONFIGURATION)
			self.__utils.changeOwnerToPath(self.__constants.PATH_FILE_CONFIGURATION, self.__constants.USER, self.__constants.GROUP)
		except (IOError, OSError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__dialog.createMessageDialog("\nError creating YAML file. For more information, see the logs.", 8, 50, "Error Message")
			self.__action_to_cancel()