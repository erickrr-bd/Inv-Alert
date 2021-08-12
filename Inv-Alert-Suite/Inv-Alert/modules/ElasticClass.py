from os import path
from sys import exit
from shutil import copy
from time import sleep, strftime
from datetime import datetime, date
from modules.UtilsClass import Utils
from ssl import create_default_context
from modules.TelegramClass import Telegram
from requests.exceptions import InvalidURL
from elasticsearch_dsl import Q, Search, A
from elasticsearch import Elasticsearch, RequestsHttpConnection, exceptions

"""
Class that manages everything related to ElasticSearch.
"""
class Elastic:
	"""
	Property that stores an object of the Utils class.
	"""
	utils = None

	"""
	Property that stores an object of the Telegram class.
	"""
	telegram = None

	"""
	Property that saves the data of the Inv-Alert
	configuration file.
	"""
	inv_alert_conf = None

	"""
	Constructor for the Elastic class.

	Parameters:
	self -- An instantiated object of the Elastic class.
	"""
	def __init__(self, inv_alert_conf):
		self.utils = Utils()
		self.telegram = Telegram()
		self.inv_alert_conf = inv_alert_conf 

	"""
	Method that creates a connection object with ElasticSearch.

	Parameters:
	self -- An instantiated object of the Elastic class.

	Return:
	conn_es -- Object that contains the connection to
			   ElasticSearch.

	Exceptions:
	KeyError -- A Python KeyError exception is what is
				raised when you try to access a key that
				isn’t in a dictionary (dict). 
	exceptions.ConnectionError --  Error raised when there
								   was an exception while
								   talking to ES. 
	exceptions.AuthenticationException -- Exception representing
										  a 401 status code.
	exceptions.AuthorizationException -- Exception representing
										 a 403 status code.
	requests.exceptions.InvalidURL -- The URL provided was
									  somehow invalid.
	"""
	def getConnectionElastic(self):
		conn_es = None
		try:
			if(not self.inv_alert_conf['use_ssl'] == True) and (not self.inv_alert_conf['use_http_auth'] == True):
				conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
										port = self.inv_alert_conf['es_port'],
										connection_class = RequestsHttpConnection,
										use_ssl = False)
			if(not self.inv_alert_conf['use_ssl'] == True) and self.inv_alert_conf['use_http_auth'] == True:
				conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
										port = self.inv_alert_conf['es_port'],
										connection_class = RequestsHttpConnection,
										http_auth = (self.utils.decryptAES(self.inv_alert_conf['http_auth_user']).decode('utf-8'), self.utils.decryptAES(self.inv_alert_conf['http_auth_pass']).decode('utf-8')),
										use_ssl = False)
			if self.inv_alert_conf['use_ssl'] == True and (not self.inv_alert_conf['use_http_auth'] == True):
				if not self.inv_alert_conf['valid_certificate']:
					conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
											port = self.inv_alert_conf['es_port'],
											connection_class = RequestsHttpConnection,
											use_ssl = True,
											verify_certs = False,
											ssl_show_warn = False)
				else:
					context = create_default_context(cafile = self.inv_alert_conf['path_certificate'])
					conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
											port = self.inv_alert_conf['es_port'],
											connection_class = RequestsHttpConnection,
											use_ssl = True,
											verify_certs = True,
											ssl_context = context)
			if self.inv_alert_conf['use_ssl'] == True and self.inv_alert_conf['use_http_auth'] == True:
				if not self.inv_alert_conf['valid_certificate'] == True:
					conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
											port = self.inv_alert_conf['es_port'],
											connection_class = RequestsHttpConnection,
											http_auth = (self.utils.decryptAES(self.inv_alert_conf['http_auth_user']).decode('utf-8'), self.utils.decryptAES(self.inv_alert_conf['http_auth_pass']).decode('utf-8')),
											use_ssl = True,
											verify_certs = False,
											ssl_show_warn = False)
				else:
					context = create_default_context(cafile = self.inv_alert_conf['path_certificate'])
					conn_es = Elasticsearch(self.inv_alert_conf['es_host'],
											port = self.inv_alert_conf['es_port'],
											connection_class = RequestsHttpConnection,
											http_auth = (self.utils.decryptAES(self.inv_alert_conf['http_auth_user']).decode('utf-8'), self.utils.decryptAES(self.inv_alert_conf['http_auth_pass']).decode('utf-8')),
											use_ssl = True,
											verify_certs = True,
											ssl_context = context)
			if not conn_es == None: 
				print("\nCONNECTION DATA:\n")
				print("Cluster name: " + conn_es.info()['cluster_name'])
				print("Elasticsearch version: " + conn_es.info()['version']['number'])
		except (KeyError, exceptions.ConnectionError, exceptions.AuthenticationException, exceptions.AuthorizationException, exceptions.RequestError, InvalidURL) as exception:
			self.utils.createInvAlertLog(exception, 3)
			print("\nFailed to connect to ElasticSearch. For more information, see the logs.")
			exit(1)
		else:
			return conn_es

	"""
	Method that obtains the inventory of a specific
	ElasticSearch index.

	Parameters:
	self -- An instantiated object of the Elastic class.
	inventory_yaml -- Object that contains all the data of
	                  a specific inventory.
	conn_es -- Object that contains the connection to
			   ElasticSearch.

	Exceptions:
	KeyError -- A Python KeyError exception is what is
				raised when you try to access a key that
				isn’t in a dictionary (dict).
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def getInventory(self, inventory_yaml, conn_es):
		now = datetime.now()
		try:
			while True:
				list_search_hosts = []
				a = A('terms', field = inventory_yaml['field_name'], size = 10000)
				search_inv = Search(index = inventory_yaml['index_name']).using(conn_es)
				if inventory_yaml['frequency_inv'] == "Daily":
					search_aux_inv = search_inv.query('range', ** { '@timestamp' : { 'gte' : "now-12h", 'lte' : "now" }}).source(fields = None)
				search_aux_inv.aggs.bucket('events', a)
				result_inv_search = search_aux_inv.execute()
				for event_found in result_inv_search.aggregations.events.buckets:
					list_search_hosts.append(event_found.key)
				path_database_file = self.utils.getPathInvAlert(self.inv_alert_conf['inv_folder']) + '/' + inventory_yaml['name_inv'] + '/database_inv.yaml'
				path_database_txt = self.utils.getPathInvAlert(self.inv_alert_conf['inv_folder']) + '/' + inventory_yaml['name_inv'] + '/inv-' + str(date.today()) + '.txt'
				if not path.exists(path_database_file):
					self.createDatabaseFile(list_search_hosts, path_database_file)
					message_telegram = self.telegram.getTelegramMessage([], [], list_search_hosts, inventory_yaml['name_inv'])
				else:
					database_yaml = self.utils.readYamlFile(path_database_file, 'rU')
					list_hosts_old = database_yaml['list_hosts']
					list_hosts_added = list(set(list_search_hosts) - set(list_hosts_old))
					list_hosts_removed = list(set(list_hosts_old) - set(list_search_hosts))
					print("\nINVENTORY NAME: " + inventory_yaml['name_inv'])
					print("Total hosts added: " + str(len(list_hosts_added)))
					print("Total hosts removed: " + str(len(list_hosts_removed)))
					if len(list_hosts_added) > 0:
						for host_to_add in list_hosts_added:
							list_hosts_old.append(host_to_add)
					if len(list_hosts_removed) > 0:
						for host_to_remove in list_hosts_removed:
							list_hosts_old.remove(host_to_remove)
					print("Total hosts: " + str(len(list_hosts_old)))
					self.createDatabaseFile(list_hosts_old, path_database_file)
					message_telegram = self.telegram.getTelegramMessage(list_hosts_added, list_hosts_removed, list_hosts_old, inventory_yaml['name_inv'])
				copy(path_database_file, path_database_txt)
				self.utils.ownerChange(path_database_txt)
				status_code_telegram = self.telegram.sendTelegramAlert(self.utils.decryptAES(inventory_yaml['telegram_chat_id']).decode('utf-8'), self.utils.decryptAES(inventory_yaml['telegram_bot_token']).decode('utf-8'), message_telegram, path_database_txt)
				self.telegram.getStatusbyResponseCode(status_code_telegram, inventory_yaml['name_inv'])
				sleep(60)
		except (KeyError, OSError, exceptions.ConnectionTimeout) as exception:
			self.utils.createInvAlertLog(exception, 3)
			print("\nFailed to get inventory. For more information, see the logs.")

	"""
	Method that creates the YAML file that will serve as the
	inventory database.

	Parameters:
	self -- An instantiated object of the Elastic class.
	list_hosts -- List with all hosts.
	path_database_file -- Path where the YAML file will be
						  created.
	"""
	def createDatabaseFile(self, list_hosts, path_database_file):
		database_json = {'last_scan_time' : strftime("%c"),
						'list_hosts' : list_hosts,
						'total_hosts' : len(list_hosts)}

		self.utils.createYamlFile(database_json, path_database_file, 'w')