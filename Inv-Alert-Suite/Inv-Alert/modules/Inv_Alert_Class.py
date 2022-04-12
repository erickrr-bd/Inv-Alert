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
		try:
			data_configuration = self.__utils.readYamlFile(self.__constants.PATH_FILE_CONFIGURATION)
			print(data_configuration)
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
				
		except (FileNotFoundError, OSError, IOError) as exception:
			print("Error")
		except (self.__elk.exceptions.AuthenticationException, self.__elk.exceptions.ConnectionError, self.__elk.exceptions.AuthorizationException, self.__elk.exceptions.RequestError) as exception:
			self.__logger.createApplicationLog(exception, 3)
			self.__logger.createApplicationLog("Error connecting to ElasticSearch. For more information, see the logs.", 3, use_stream_handler = True)
			exit(1)