from os import path
from sys import exit
from threading import Thread
from libPyElk import libPyElk
from libPyLog import libPyLog
from time import sleep, strftime
from libPyUtils import libPyUtils
from datetime import datetime, date
from .Constants_Class import Constants
from libPyTelegram import libPyTelegram

"""
Class that manages everything related to Inv-Alert.
"""
class InvAlert:
	"""
	Attribute that stores an object of the libPyUtils class.
	"""
	__utils = None

	"""
	Attribute that stores an object of the libPyLog class.
	"""
	__logger = None

	"""
	Attribute that stores an object of the libPyTelegram class.
	"""
	__telegram = None

	"""
	Attribute that stores an object of the Constants class.
	"""
	__constants = None

	"""
	Attribute that stores an object of the libPyElk class.
	"""
	__elasticsearch = None


	def __init__(self):
		"""
		Method that corresponds to the constructor of the class.
		"""
		self.__logger = libPyLog()
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__elasticsearch = libPyElk()
		self.__telegram = libPyTelegram()


	def startInvAlert(self):
		"""
		Method that starts the operation of Inv-Alert.
		"""
		try:
			data_configuration = self.__utils.readYamlFile(self.__constants.PATH_FILE_CONFIGURATION)
			if data_configuration["use_http_authentication"] == True:
				conn_es = self.__elasticsearch.createConnectionToElasticSearch(data_configuration, path_key_file = self.__constants.PATH_KEY_FILE)
			else:
				conn_es = self.__elasticsearch.createConnectionToElasticSearch(data_configuration)
			if not conn_es == None:
				self.__logger.generateApplicationLog("Inv-Alert v3.2", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("@2022 Tekium. All rights reserved.", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("Author: Erick Rodriguez", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("Email: erodriguez@tekium.mx, erickrr.tbd93@gmail.com", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("License: GPLv3", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("Inv-Alert started", 1, "__start", use_stream_handler = True)
				self.__logger.generateApplicationLog("Established connection with: " + data_configuration["es_host"] + ":" + str(data_configuration["es_port"]), 1, "__connection" , use_stream_handler = True)
				self.__logger.generateApplicationLog("Elasticsearch Cluster Name: " + conn_es.info()["cluster_name"], 1, "__connection", use_stream_handler = True)
				self.__logger.generateApplicationLog("Elasticsearch Version: " + conn_es.info()["version"]["number"], 1, "__connection", use_stream_handler = True)
				list_all_inventories = self.__utils.getListToAllSubDirectories(self.__constants.PATH_INVENTORIES_FOLDER)
				if list_all_inventories:
					self.__logger.generateApplicationLog(str(len(list_all_inventories)) + " inventories in: " + self.__constants.PATH_INVENTORIES_FOLDER, 1, "__readInventories", use_stream_handler = True)
					for inventory in list_all_inventories:
						self.__logger.generateApplicationLog(inventory + " load", 1, "__inventory", use_stream_handler = True)
						data_inventory = self.__utils.readYamlFile(self.__constants.PATH_INVENTORIES_FOLDER + "/" + inventory + "/" + inventory + ".yaml")
						Thread(name = inventory, target = self.__getInventory, args = (data_inventory, conn_es, )).start()
		except KeyError as exception:
			self.__logger.generateApplicationLog("Key Error: " + str(exception), 3, "__start", use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)
		except (FileNotFoundError, OSError, IOError) as exception:
			self.__logger.generateApplicationLog("Error to open or read a file or directory. For more information, see the logs.", 3, "__start", use_stream_handler = True)
			self.__logger.generateApplicationLog(exception, 3, "__start", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)
		except (self.__elasticsearch.exceptions.AuthenticationException, self.__elasticsearch.exceptions.ConnectionError, self.__elasticsearch.exceptions.AuthorizationException, self.__elasticsearch.exceptions.RequestError, self.__elasticsearch.exceptions.ConnectionTimeout) as exception:
			self.__logger.generateApplicationLog("Error connecting to ElasticSearch. For more information, see the logs.", 3, "__connection", use_stream_handler = True)
			self.__logger.generateApplicationLog(exception, 3, "__connection", use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)


	def __getInventory(self, data_inventory, conn_es):
		"""
		Method that is obtaining the inventory of the day.

		:arg data_inventory (dict): Object that contains the inventory data.
		:arg conn_es (object): Object that contains a connection to ElasticSearch.
		"""
		try:
			search_in_elastic = self.__elasticsearch.createSearchObject(conn_es, data_inventory["index_pattern_name"])
			inventory_time_execution = data_inventory["inventory_time_execution"].split(':')
			passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
			telegram_bot_token = self.__utils.decryptDataWithAES(data_inventory["telegram_bot_token"], passphrase).decode("utf-8")
			telegram_chat_id = self.__utils.decryptDataWithAES(data_inventory["telegram_chat_id"], passphrase).decode("utf-8")
			while True:
				now = datetime.now()
				if (now.hour == int(inventory_time_execution[0]) and now.minute == int(inventory_time_execution[1])):
					list_all_hosts_found = []
					result_search = self.__elasticsearch.executeSearchWithAggregation(search_in_elastic, data_inventory["field_name_in_index"], "now-1d", "now")
					for bucket in result_search.aggregations.events.buckets:
						list_all_hosts_found.append(bucket.key)
					path_inventory_yaml = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory["inventory_name"] + '/' + "database_inventory.yaml"
					path_inventory_txt = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory["inventory_name"] + '/' + data_inventory["inventory_name"] + '-' + str(date.today()) + ".txt"
					if not path.exists(path_inventory_yaml):
						self.__createDatabaseYamlFile(list_all_hosts_found, path_inventory_yaml)
						message_to_send = self.__generateMessageTelegram(data_inventory["inventory_name"], [], [], list_all_hosts_found)
						self.__logger.generateApplicationLog("Total hosts: " + str(len(list_all_hosts_found)), 1, "__" + data_inventory["inventory_name"], use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
					else:
						database_inventory = self.__utils.readYamlFile(path_inventory_yaml)
						list_all_hosts_actual = database_inventory["list_all_hosts_found"]
						list_all_hosts_added = list(set(list_all_hosts_found) - set(list_all_hosts_actual))
						list_all_hosts_removed = list(set(list_all_hosts_actual) - set(list_all_hosts_found))
						self.__logger.generateApplicationLog("Total hosts added: " + str(len(list_all_hosts_added)), 1, "__" + data_inventory["inventory_name"], use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
						self.__logger.generateApplicationLog("Total hosts removed: " + str(len(list_all_hosts_removed)), 1, "__" + data_inventory["inventory_name"], use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
						if list_all_hosts_added:
							list_all_hosts_actual.extend(list_all_hosts_added)
						if list_all_hosts_removed:
							for host in list_all_hosts_removed:
								list_all_hosts_actual.remove(host)
						self.__logger.generateApplicationLog("Total hosts: " + str(len(list_all_hosts_actual)), 1, "__" + data_inventory["inventory_name"], use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
						self.__createDatabaseYamlFile(list_all_hosts_actual, path_inventory_yaml)
						message_to_send = self.__generateMessageTelegram(data_inventory["inventory_name"], list_all_hosts_added, list_all_hosts_removed, list_all_hosts_actual)
					self.__utils.copyFile(path_inventory_yaml, path_inventory_txt)
					self.__utils.changeOwnerToPath(path_inventory_txt, self.__constants.USER, self.__constants.GROUP)
					response_status_code = self.__telegram.sendFileMessageTelegram(telegram_bot_token, telegram_chat_id, message_to_send, path_inventory_txt)
					self.__createLogByTelegramCode(response_status_code, data_inventory["inventory_name"])
				sleep(60)
		except KeyError as exception:
			self.__logger.generateApplicationLog("Key Error: " + str(exception), 3, "__" + data_inventory["inventory_name"], use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)
		except ValueError as exception:
			self.__logger.generateApplicationLog("Error to encrypt or decrypt the data. For more information, see the logs.", 3, "__" + data_inventory["inventory_name"], use_stream_handler = True)
			self.__logger.generateApplicationLog(exception, 3, "__" + data_inventory["inventory_name"], use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)
		except (OSError, IOError, FileNotFoundError) as exception:
			self.__logger.generateApplicationLog("Error to create, open or read a file or directory. For more information, see the logs.", 3, "__" + data_inventory["inventory_name"], use_stream_handler = True)
			self.__logger.generateApplicationLog(exception, 3, "__" + data_inventory["inventory_name"], use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)
		except (self.__elasticsearch.exceptions.AuthenticationException, self.__elasticsearch.exceptions.ConnectionError, self.__elasticsearch.exceptions.AuthorizationException, self.__elasticsearch.exceptions.RequestError, self.__elasticsearch.exceptions.ConnectionTimeout) as exception:
			self.__logger.generateApplicationLog("Error performing an action in ElasticSearch. For more information, see the logs.", 3, "__" + data_inventory["inventory_name"], use_stream_handler = True)
			self.__logger.generateApplicationLog(exception, 3, "__" + data_inventory["inventory_name"], use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
			exit(1)


	def __createDatabaseYamlFile(self, list_all_hosts_found, path_inventory_yaml):
		"""
		Method that creates the YAML file where the list of hosts obtained will be stored.

		:arg list_all_hosts_found (list): List containing the name of all obtained hosts.
		:arg path_inventory_yaml (string): Absolute path of the YAML file corresponding to the list of hosts.
		"""
		database_inventory_json = {"last_scan_time" : strftime("%c"),
								   "list_all_hosts_found" : list_all_hosts_found,
								   "total_hosts_found" : len(list_all_hosts_found)}

		self.__utils.createYamlFile(database_inventory_json, path_inventory_yaml)
		self.__utils.changeOwnerToPath(path_inventory_yaml, self.__constants.USER, self.__constants.GROUP)


	def __generateMessageTelegram(self, inventory_name, list_all_hosts_added, list_all_hosts_removed, list_all_hosts_actual):
		"""
		Method that generates the message to be sent via Telegram.

		Return the string that will be send to Telegram.

		:arg inventory_name (string): Inventory name.
		:arg list_all_hosts_added (list): List with all the names of the added hosts.
		:arg list_all_hosts_removed (list): List with all the names of the removed hosts.
		:arg list_all_hosts_actual (list): List with all the names of the final or current hosts.
		"""
		message_telegram = "" + u"\u26A0\uFE0F" + " " + inventory_name +  " " + u"\u26A0\uFE0F" + "\n\n" + u"\u23F0" + " Alert sent: " + strftime("%c") + "\n\n"
		message_telegram += u"\u270F\uFE0F" + " Total hosts added: " + str(len(list_all_hosts_added)) + "\n"
		if list_all_hosts_added:
			for host in list_all_hosts_added:
				message_telegram += "\n" + u"\u2611\uFE0F" + " " + host
		message_telegram += "\n\n" + u"\u270F\uFE0F" + " Total hosts removed: " + str(len(list_all_hosts_removed)) + "\n"
		if list_all_hosts_removed:
			for host in list_all_hosts_removed:
				message_telegram += "\n" + u"\u2611\uFE0F" + " " + host
		message_telegram += "\n\n" + "TOTAL HOSTS: " + str(len(list_all_hosts_actual))
		if len(message_telegram) > 1024:
			message_telegram = "" + u"\u26A0\uFE0F" + " " + inventory_name +  " " + u"\u26A0\uFE0F" + "\n\n" + u"\u23F0" + " Alert sent: " + strftime("%c") + "\n\n"
			message_telegram += u"\u270F\uFE0F" + " Total hosts added: " + str(len(list_all_hosts_added)) + "\n"
			message_telegram += "\n\n" + u"\u270F\uFE0F" + " Total hosts removed: " + str(len(list_all_hosts_removed))
			message_telegram += "\n\n" + "TOTAL HOSTS: " + str(len(list_all_hosts_actual))
		return message_telegram.encode("utf-8")


	def __createLogByTelegramCode(self, response_status_code, inventory_name):
		"""
		Method that creates a log based on the HTTP code received as a response.

		:arg response_status_code (integer): HTTP code received in the response when sending the alert to Telegram.
		:arg inventory_name (string): Name of the inventory from which the alert was sent.
		"""
		if response_status_code == 200:
			self.__logger.generateApplicationLog("Telegram message sent.", 1, "__" + inventory_name, use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
		elif response_status_code == 400:
			self.__logger.generateApplicationLog("Telegram message not sent. Status: Bad request.", 3, "__" + inventory_name, use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
		elif response_status_code == 401:
			self.__logger.generateApplicationLog("Telegram message not sent. Status: Unauthorized.", 3, "__" + inventory_name, use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)
		elif response_status_code == 404:
			self.__logger.generateApplicationLog("Telegram message not sent. Status: Not found.", 3, "__" + inventory_name, use_stream_handler = True, use_file_handler = True, name_file_log = self.__constants.NAME_FILE_LOG, user = self.__constants.USER, group = self.__constants.GROUP)