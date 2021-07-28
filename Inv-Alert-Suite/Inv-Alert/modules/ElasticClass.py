import requests
from os import path
from sys import exit
from datetime import datetime
from time import sleep, strftime
from modules.UtilsClass import Utils
from ssl import create_default_context
from elasticsearch_dsl import Q, Search, A
from elasticsearch import Elasticsearch, RequestsHttpConnection, exceptions

"""
Class that manages everything related to ElasticSearch.
"""
class Elastic:
	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Property that stores an object of type Utils.
	"""
	inv_alert_conf = None

	"""
	Constructor for the Elastic class.

	Parameters:
	self -- An instantiated object of the Elastic class.
	"""
	def __init__(self, inv_alert_conf):
		self.utils = Utils()
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
		except (KeyError, exceptions.ConnectionError, exceptions.AuthenticationException, exceptions.AuthorizationException, requests.exceptions.InvalidURL) as exception:
			self.utils.createInvAlertLog(exception, 3)
			print("\nFailed to connect to ElasticSearch. For more information, see the logs.")
			exit(1)
		else:
			return conn_es

	"""
	Method that establishes the connection of Telk-Alert with ElasticSearch.

	Parameters:
	self -- An instantiated object of the Elastic class.
	telk_alert_conf -- List containing all the information in the Telk-Alert configuration file.

	Return:
	conn_es -- Object that contains the connection to ElasticSearch.

	
	"""

	def getInventory(self, inventory_yaml, conn_es):
		now = datetime.now()
		try:
			while True:
				list_search_hosts = []
				a = A('terms', field = inventory_yaml['field_name'], size = 10000)
				search_inv = Search(index = inventory_yaml['index_name']).using(conn_es)
				if inventory_yaml['frequency_inv'] == "Daily":
					search_aux_inv = search_inv.query('range', ** { '@timestamp' : { 'gte' : "now-1d", 'lte' : "now" }}).source(fields = None)
				search_aux_inv.aggs.bucket('events', a)
				result_inv_search = search_aux_inv.execute()
				for event_found in result_inv_search.aggregations.events.buckets:
					list_search_hosts.append(event_found.key)
				if not path.exists(self.utils.getPathInvAlert(self.inv_alert_conf['inv_folder']) + '/' + inventory_yaml['name_inv'] + '/database_inv.yaml'):
					self.createDatabaseFile(list_search_hosts)
				else:
					print("Si existe")
				sleep(60)
		except (KeyError, OSError) as exception:
			print("Error")

	def createDatabaseFile(self, list_hosts):
		database_json = {'last_scan_time' : strftime("%c"),
						'list_hosts' : list_hosts,
						'total_hosts' : len(list_hosts)}

		print(database_json)