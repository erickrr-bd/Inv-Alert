from sys import exit
from threading import Thread
from datetime import datetime
from libPyElk import libPyElk
from libPyLog import libPyLog
from libPyUtils import libPyUtils
from .Constants_Class import Constants

class InvAlert:

	__elk = None

	__utils = None

	__logger = None

	__constants = None

	def __init__(self):
		self.__elk = libPyElk()
		self.__utils = libPyUtils()
		self.__constants = Constants()
		self.__logger = libPyLog(self.__constants.NAME_FILE_LOG, self.__constants.NAME_LOG, self.__constants.USER, self.__constants.GROUP)


	def startInvAlert(self):
		"""
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
						thread_inventory = Thread(name = inventory, target = self.getInventory, args = (data_inventory, conn_es, )).start()
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

	def getInventory(self, data_inventory, conn_es):
		try:
			inventory_time_execution = data_inventory['inventory_time_execution']
			while True:
				now = datetime.now()
				list_all_hosts_found = []
				result_search = self.__elk.searchAggregationsTermsElasticSearch(conn_es, data_inventory['index_pattern_name'], data_inventory['field_name_in_index'])
				for bucket in result_search.aggregations.events.buckets:
					list_all_hosts_found.append(bucket.key)
				print(list_all_hosts_found)
		except KeyError as exception:
			print("KeyError")