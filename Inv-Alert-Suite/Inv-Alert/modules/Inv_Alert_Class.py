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
	Attribute that stores an object of the libPyElk class.
	"""
	__elk = None

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


	def __init__(self):
		"""
		Method that corresponds to the constructor of the class.
		"""
		self.__elk = libPyElk()
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__telegram = libPyTelegram()
		self.__logger = libPyLog(self.__constants.NAME_FILE_LOG, self.__constants.NAME_LOG, self.__constants.USER, self.__constants.GROUP)


	def startInvAlert(self):
		"""
		Method that starts the operation of Inv-Alert.
		"""
		try:
			data_configuration = self.__utils.readYamlFile(self.__constants.PATH_FILE_CONFIGURATION)
			if data_configuration['use_http_authentication'] == True:
				conn_es = self.__elk.createConnectionToElasticSearch(data_configuration, path_key_file = self.__constants.PATH_KEY_FILE)
			else:
				conn_es = self.__elk.createConnectionToElasticSearch(data_configuration)
			if not conn_es == None:
				self.__logger.createApplicationLog("Inv-Alert v3.1", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("@2022 Tekium. All rights reserved.", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Author: Erick Rodriguez", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Email: erodriguez@tekium.mx, erickrr.tbd93@gmail.com", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("License: GPLv3", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Inv-Alert started...", 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Established connection with: " + data_configuration['es_host'] + ':' + str(data_configuration['es_port']), 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Cluster name: " + conn_es.info()['cluster_name'], 1, use_stream_handler = True)
				self.__logger.createApplicationLog("Elasticsearch version: " + conn_es.info()['version']['number'], 1, use_stream_handler = True)
				list_all_inventories = self.__utils.getListToAllSubDirectories(self.__constants.PATH_INVENTORIES_FOLDER)
				if not list_all_inventories:
					self.__logger.createApplicationLog("No inventories were found in: " + self.__constants.PATH_INVENTORIES_FOLDER, 2, use_stream_handler = True)
					exit(1)
				else:
					self.__logger.createApplicationLog("Inventories path: " + self.__constants.PATH_INVENTORIES_FOLDER, 1, use_stream_handler = True)
					self.__logger.createApplicationLog("Total inventories found: " + str(len(list_all_inventories)), 1, use_stream_handler = True)
					for inventory in list_all_inventories:
						self.__logger.createApplicationLog(inventory + " loaded.", 1, use_stream_handler = True)
						data_inventory = self.__utils.readYamlFile(self.__constants.PATH_INVENTORIES_FOLDER + '/' + inventory + '/' + inventory + ".yaml")
						thread_inventory = Thread(name = inventory, target = self.__getInventory, args = (data_inventory, conn_es, )).start()
		except KeyError as exception:
			self.__logger.createApplicationLog("Key Error: " + str(exception), 3, use_stream_handler = True)
			exit(1)
		except (FileNotFoundError, OSError, IOError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__logger.createApplicationLog("Error opening or reading the file. For more information, see the logs.", 3, use_stream_handler = True)
			exit(1)
		except (self.__elk.exceptions.AuthenticationException, self.__elk.exceptions.ConnectionError, self.__elk.exceptions.AuthorizationException, self.__elk.exceptions.RequestError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__logger.createApplicationLog("Error connecting to ElasticSearch. For more information, see the logs.", 3, use_stream_handler = True)
			exit(1)


	def __getInventory(self, data_inventory, conn_es):
		"""
		Method that is in charge of obtaining the inventory of the day and carrying out the corresponding operations.

		:arg data_inventory: Object that contains the inventory data.
		:arg conn_es: Object that contains a connection to ElasticSearch.
		"""
		try:
			inventory_time_execution = data_inventory['inventory_time_execution'].split(':')
			while True:
				now = datetime.now()
				if (now.hour == int(inventory_time_execution[0]) and now.minute == int(inventory_time_execution[1])):
					list_all_hosts_found = []
					result_search = self.__elk.searchAggregationsTermsElasticSearch(conn_es, data_inventory['index_pattern_name'], data_inventory['field_name_in_index'])
					for bucket in result_search.aggregations.events.buckets:
						list_all_hosts_found.append(bucket.key)
					path_inventory_yaml = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory['inventory_name'] + '/' + "database_inventory.yaml"
					path_inventory_txt = self.__constants.PATH_INVENTORIES_FOLDER + '/' + data_inventory['inventory_name'] + '/' + data_inventory['inventory_name'] + '-' + str(date.today()) + ".txt"
					self.__logger.createApplicationLog("Inventory name: " + data_inventory['inventory_name'], 1, use_stream_handler = True)
					if not path.exists(path_inventory_yaml):
						self.__createDatabaseYamlFile(list_all_hosts_found, path_inventory_yaml)
						message_to_send = self.__getTelegramMessage(data_inventory['inventory_name'], [], [], list_all_hosts_found)
						self.__logger.createApplicationLog("Total hosts: " + str(len(list_all_hosts_found)), 1, use_stream_handler = True)
					else:
						database_inventory = self.__utils.readYamlFile(path_inventory_yaml)
						list_all_hosts_actual = database_inventory['list_all_hosts_found']
						list_all_hosts_added = list(set(list_all_hosts_found) - set(list_all_hosts_actual))
						list_all_hosts_removed = list(set(list_all_hosts_actual) - set(list_all_hosts_found))
						self.__logger.createApplicationLog("Total hosts added: " + str(len(list_all_hosts_added)), 1, use_stream_handler = True)
						self.__logger.createApplicationLog("Total hosts removed: " + str(len(list_all_hosts_removed)), 1, use_stream_handler = True)
						if list_all_hosts_added:
							list_all_hosts_actual.extend(list_all_hosts_added)
						if list_all_hosts_removed:
							for host in list_all_hosts_removed:
								list_all_hosts_actual.remove(host)
						self.__logger.createApplicationLog("Total hosts: " + str(len(list_all_hosts_actual)), 1, use_stream_handler = True)
						self.__createDatabaseYamlFile(list_all_hosts_actual, path_inventory_yaml)
						message_to_send = self.__getTelegramMessage(data_inventory['inventory_name'], list_all_hosts_added, list_all_hosts_removed, list_all_hosts_actual)
					self.__utils.copyFile(path_inventory_yaml, path_inventory_txt)
					self.__utils.changeOwnerToPath(path_inventory_txt, self.__constants.USER, self.__constants.GROUP)
					passphrase = self.__utils.getPassphraseKeyFile(self.__constants.PATH_KEY_FILE)
					telegram_bot_token = self.__utils.decryptDataWithAES(data_inventory['telegram_bot_token'], passphrase).decode('utf-8')
					telegram_chat_id = self.__utils.decryptDataWithAES(data_inventory['telegram_chat_id'], passphrase).decode('utf-8')
					status_code_telegram = self.__telegram.sendFileMessageTelegram(telegram_bot_token, telegram_chat_id, message_to_send, path_inventory_txt)
					self.__createLogByTelegramCode(status_code_telegram)
				sleep(60)
		except KeyError as exception:
			self.__logger.createApplicationLog("Key Error: " + str(exception), 3, use_stream_handler = True)
			exit(1)
		except (self.__elk.exceptions.ConnectionTimeout, self.__elk.exceptions.RequestError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__logger.createApplicationLog("Failed to get inventory. For more information, see the logs.", 3, use_stream_handler = True)
			exit(1)
		except (OSError, IOError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__logger.createApplicationLog("Error creating, opening or reading the file. For more information, see the logs.", 3, use_stream_handler = True)
			exit(1)


	def __createDatabaseYamlFile(self, list_all_hosts_found, path_inventory_yaml):
		"""
		Method that creates the YAML file where the list of hosts obtained will be stored.

		:arg list_all_hosts_found: List containing the name of all obtained hosts.
		:arg path_inventory_yaml: Absolute path of the YAML file corresponding to the list of hosts.
		"""
		database_inventory_json = {'last_scan_time' : strftime("%c"),
								   'list_all_hosts_found' : list_all_hosts_found,
								   'total_hosts_found' : len(list_all_hosts_found)}

		self.__utils.createYamlFile(database_inventory_json, path_inventory_yaml)
		self.__utils.changeOwnerToPath(path_inventory_yaml, self.__constants.USER, self.__constants.GROUP)


	def __getTelegramMessage(self, inventory_name, list_all_hosts_added, list_all_hosts_removed, list_all_hosts_actual):
		"""
		Method that generates the message to be sent via Telegram.

		:arg inventory_name: Inventory name.
		:arg list_all_hosts_added: List with all the names of the added hosts.
		:arg list_all_hosts_removed: List with all the names of the removed hosts.
		:arg list_all_hosts_actual: List with all the names of the final or current hosts.
		"""
		message_telegram = "" + u'\u26A0\uFE0F' + " " + inventory_name +  " " + u'\u26A0\uFE0F' + '\n\n' + u'\u23F0' + " Alert sent: " + strftime("%c") + "\n\n"
		message_telegram += u'\u270F\uFE0F' + " Total hosts added: " + str(len(list_all_hosts_added)) + '\n'
		if list_all_hosts_added:
			for host in list_all_hosts_added:
				message_telegram += '\n' + u'\u2611\uFE0F' + ' ' + host
		message_telegram += '\n\n' + u'\u270F\uFE0F' + " Total hosts removed: " + str(len(list_all_hosts_removed)) + '\n'
		if list_all_hosts_removed:
			for host in list_all_hosts_removed:
				message_telegram += '\n' + u'\u2611\uFE0F' + ' ' + host
		message_telegram += '\n\n' + "TOTAL HOSTS: " + str(len(list_all_hosts_actual))
		if len(message_telegram) > 1024:
			message_telegram = "" + u'\u26A0\uFE0F' + " " + inventory_name +  " " + u'\u26A0\uFE0F' + '\n\n' + u'\u23F0' + " Alert sent: " + strftime("%c") + "\n\n"
			message_telegram += u'\u270F\uFE0F' + " Total hosts added: " + str(len(list_all_hosts_added)) + '\n'
			message_telegram += '\n\n' + u'\u270F\uFE0F' + " Total hosts removed: " + str(len(list_all_hosts_removed))
			message_telegram += '\n\n' + "TOTAL HOSTS: " + str(len(list_all_hosts_actual))
		return message_telegram.encode('utf-8')


	def __createLogByTelegramCode(self, response_http_code):
		"""
		Method that creates a log based on the HTTP code received as a response.

		:arg response_http_code: HTTP code received in the response when sending the alert to Telegram.
		"""
		if response_http_code == 200:
			self.__logger.createApplicationLog("Telegram message sent.", 1, use_stream_handler = True)
		elif response_http_code == 400:
			self.__logger.createApplicationLog("Telegram message not sent. Status: Bad request.", 3, use_stream_handler = True)
		elif response_http_code == 401:
			self.__logger.createApplicationLog("Telegram message not sent. Status: Unauthorized.", 3, use_stream_handler = True)
		elif response_http_code == 404:
			self.__logger.createApplicationLog("Telegram message not sent. Status: Not found.", 3, use_stream_handler = True)