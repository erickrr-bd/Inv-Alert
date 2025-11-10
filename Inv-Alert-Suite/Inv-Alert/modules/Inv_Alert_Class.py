"""
Class that manages everything related to Inv-Alert.
"""
from os import path
from threading import Thread
from libPyLog import libPyLog
from libPyElk import libPyElk
from time import sleep, strftime
from libPyUtils import libPyUtils
from datetime import datetime, date
from .Constants_Class import Constants
from libPyTelegram import libPyTelegram
from dataclasses import dataclass, field
from libPyConfiguration import libPyConfiguration

@dataclass
class InvAlert:

	logger: libPyLog = field(default_factory = libPyLog)
	utils: libPyUtils = field(default_factory = libPyUtils)
	constants: Constants = field(default_factory = Constants)
	elasticsearch: libPyElk = field(default_factory = libPyElk)
	telegram: libPyTelegram = field(default_factory = libPyTelegram)


	def start_inv_alert(self) -> None:
		"""
		Method that starts Inv-Alert.
		"""
		try:
			self.logger.create_log("Author: Erick Roberto Rodríguez Rodríguez", 2, "_start", use_stream_handler = True)
			self.logger.create_log("Email: erickrr.tbd93@gmail.com, erodriguez@tekium.mx", 2, "_start", use_stream_handler = True)
			self.logger.create_log("Github: https://github.com/erickrr-bd/Inv-Alert", 2, "_start", use_stream_handler = True)
			self.logger.create_log("Inv-Alert v3.3 - November 2025", 2, "_start", use_stream_handler = True)
			if path.exists(self.constants.INV_ALERT_CONFIGURATION):
				self.logger.create_log(f"Configuration found: {self.constants.INV_ALERT_CONFIGURATION}", 2, "_readConfiguration", use_stream_handler = True)
				configuration = libPyConfiguration()
				data = self.utils.read_yaml_file(self.constants.INV_ALERT_CONFIGURATION)
				configuration.convert_dict_to_object(data)
				if configuration.use_authentication:
					if configuration.authentication_method == "HTTP Authentication":
						conn_es = self.elasticsearch.create_connection_http_auth(configuration, self.constants.KEY_FILE)
					elif configuration.authentication_method == "API Key":
						conn_es = self.elasticsearch.create_connection_api_key(configuration, self.constants.KEY_FILE)
				else:
					conn_es = self.elasticsearch.create_connection_without_auth(configuration)
				self.logger.create_log(f"Connection established: {','.join(configuration.es_host)}", 2, "_clusterConnection", use_stream_handler = True)
				self.logger.create_log(f"ElasticSearch Cluster Name: {conn_es.info()["cluster_name"]}", 2, "_clusterConnection", use_stream_handler = True)
				self.logger.create_log(f"ElasticSearch Cluster UUID: {conn_es.info()["cluster_uuid"]}", 2, "_clusterConnection", use_stream_handler = True)
				self.logger.create_log(f"ElasticSearch Version: {conn_es.info()["version"]["number"]}", 2, "_clusterConnection", use_stream_handler = True)
				if configuration.use_authentication:
					self.logger.create_log("Authentication enabled", 2, "_clusterConnection", use_stream_handler = True)
					self.logger.create_log("Authentication Method: HTTP Authentication", 2, "_clusterConnection", use_stream_handler = True) if configuration.authentication_method == "HTTP Authentication" else self.logger.create_log("Authentication Method: API Key", 2, "_clusterConnection", use_stream_handler = True)
				else:
					self.logger.create_log("Authentication disabled. Not recommended for security reasons.", 3, "_clusterConnection", use_stream_handler = True)
				if configuration.verificate_certificate_ssl:
					self.logger.create_log("SSL Certificate verification enabled", 2, "_clusterConnection", use_stream_handler = True)
					self.logger.create_log(f"SSL Certificate: {configuration.certificate_file}", 2, "_clusterConnection", use_stream_handler = True)
				else:
					self.logger.create_log("Certificate verification disabled. Not recommended for security reasons.", 3, "_clusterConnection", use_stream_handler = True)
				inventories = self.utils.get_enabled_subdirectories(self.constants.INVENTORIES_FOLDER)
				if inventories:
					self.logger.create_log(f"{str(len(inventories))} inventories in: {self.constants.INVENTORIES_FOLDER}", 2 , "_readInventories", use_stream_handler = True)
					for inventory in inventories:
						inventory_data = self.utils.read_yaml_file(f"{self.constants.INVENTORIES_FOLDER}/{inventory}/{inventory}.yaml")
						self.logger.create_log(f"Inventory: {inventory_data["name"]}", 2, "_loadInventory", use_stream_handler = True)
						Thread(name = inventory[:-5], target = self.start_inventory, args = (conn_es, inventory_data)).start()
				else:
					self.logger.create_log(f"No inventories in: {self.constants.INVENTORIES_FOLDER}", 3, "_readInventories", use_stream_handler = True)
			else:
				self.logger.create_log("Configuration not found.", 4, "_readConfiguration", use_stream_handler = True)
		except Exception as exception:
			self.logger.create_log("Error starting Inv-Alert. For more information, see the logs.", 4, "_start", use_stream_handler = True)
			self.logger.create_log(exception, 4, "_start", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def start_inventory(self, conn_es, inventory_data: dict) -> None:
		"""
		Method that executes an inventory.

		Parameters:
			conn_es (ElasticSearch): A straightforward mapping from Python to ES REST endpoints.
			inventory_data (dict): Object that contains the inventory's configuration data.
		"""
		try:
			execution_time = inventory_data["execution_time"].split(':')
			passphrase = self.utils.get_passphrase(self.constants.KEY_FILE)
			telegram_bot_token = self.utils.decrypt_data(inventory_data["telegram_bot_token"], passphrase).decode("utf-8")
			telegram_chat_id = self.utils.decrypt_data(inventory_data["telegram_chat_id"], passphrase).decode("utf-8")
			while True:
				now = datetime.now()
				if (now.hour == int(execution_time[0]) and now.minute == int(execution_time[1])):
					hosts_list = []
					inventory_yaml = f"{self.constants.INVENTORIES_FOLDER}/{inventory_data["name"]}/inventory.yaml"
					inventory_txt = f"{self.constants.INVENTORIES_FOLDER}/{inventory_data["name"]}/{inventory_data["name"]}-{date.today()}.txt"
					result = self.elasticsearch.search_multiple_aggregation(conn_es, inventory_data["index_pattern"], inventory_data["timestamp_field"], inventory_data["hostname_field"], inventory_data["ip_address_field"], "now-1d", "now")
					for bucket in result.aggregations.events.buckets:
						hits = bucket.events_two.hits.hits[0]._source.to_dict()
						ip_list = self.get_nested_value(hits, inventory_data["ip_address_field"])
						hosts_list.append((bucket.key, ip_list))
					if not path.exists(inventory_yaml):
						self.create_inventory_yaml(hosts_list, inventory_yaml)
						telegram_message = self.generate_telegram_message([], [], hosts_list, inventory_data["name"])
						self.logger.create_log(f"Total hosts: {len(hosts_list)}", 2, f"_{inventory_data["name"]}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
					else:
						inventory_yaml_data = self.utils.read_yaml_file(inventory_yaml)
						current_hosts = inventory_yaml_data["hosts_list"]
						hosts_list = [(host, tuple(ips)) for host, ips in hosts_list]
						current_hosts = [(host, tuple(ips)) for host, ips in current_hosts]
						added_hosts = list(set(hosts_list) - set(current_hosts))
						removed_hosts = list(set(current_hosts) - set(hosts_list))
						self.logger.create_log(f"Added Hosts: {len(added_hosts)}", 2, f"_{inventory_data["name"]}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
						self.logger.create_log(f"Removed Hosts: {len(removed_hosts)}", 2, f"_{inventory_data["name"]}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
						if added_hosts:
							current_hosts.extend(added_hosts)
						if removed_hosts:
							[current_hosts.remove(host) for host in removed_hosts]
						self.logger.create_log(f"Total hosts: {len(current_hosts)}", 2, f"_{inventory_data["name"]}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
						self.create_inventory_yaml(current_hosts, inventory_yaml)
						telegram_message = self.generate_telegram_message(added_hosts, removed_hosts, current_hosts, inventory_data["name"])
					self.utils.convert_yaml_to_txt(inventory_yaml, inventory_txt)
					response_http_code = self.telegram.send_telegram_message_and_file(telegram_bot_token, telegram_chat_id, telegram_message, inventory_txt)
					self.create_log_by_telegram_code(response_http_code, inventory_data["name"])
				sleep(60)
		except Exception as exception:
			self.logger.create_log(f"Error running the inventory: {inventory_data["name"]}. For more information, see the logs.", 4, f"_{inventory_data["name"]}", use_stream_handler = True)
			self.logger.create_log(exception, 4, f"_{inventory_data["name"]}", use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)


	def get_nested_value(self, hits: dict, field_name: str, default = None) -> str:
		"""
		Method that obtains the values of an aggregation when the field's name has the character '.'.

		Parameters:
			hits (list): Search result by aggregation.
			field_name (str): Field's name.
			default (str): Default value.

		Returns:
			value (list): Value's list. 
		"""
		keys = field_name.split('.')
		value = hits
		for key in keys:
			if isinstance(value, dict) and key in value:
				value = value[key]
			else:
				return default
		return value


	def create_inventory_yaml(self, hosts_list: dict, inventory_yaml: str) -> None:
		"""
		Method that saves the host inventory in a YAML file.

		Parameters:
			hosts_list (list): List with the total number of hosts.
			inventory_yaml (str): Inventory's yaml file.
		"""
		inventory_yaml_json = {
			"last_scan_time" : strftime("%c"),
			"hosts_list" : hosts_list,
			"total_hosts" : len(hosts_list)
		}
		self.utils.create_yaml_file(inventory_yaml_json, inventory_yaml)
		self.utils.change_owner(inventory_yaml, self.constants.USER, self.constants.GROUP, "640")


	def generate_telegram_message(self, added_hosts: list, removed_hosts: list, total_hosts: list, inventory_name: str) -> str:
		"""
		Method that generates the message to be sent via Telegram.

		Parameters:
			added_hosts (list): List with the total hosts added.
			removed_hosts (list): List with the total number of hosts removed.
			total_hosts (list): List with the total number of hosts.
			inventory_name (str): Inventory's name.

		Returns:
			telegram_message (str): Message to be sent via Telegram.
		"""
		emoji_alert = "\u26A0\uFE0F"
		emoji_clock = "\u23F0"	
		emoji_pencil = "\u270F\uFE0F"
		emoji_check = "\u2611\uFE0F"
		
		telegram_message = f"{emoji_alert} {inventory_name} {emoji_alert}\n\n{emoji_clock} Alert sent: {strftime("%c")}\n\n"
		telegram_message += f"{emoji_pencil} Added Hosts: {len(added_hosts)}\n"
		if added_hosts:
			for host in added_hosts:
				telegram_message += f"\n{emoji_check} {host[0]}"
		telegram_message += f"\n\n{emoji_pencil} Removed Hosts: {len(removed_hosts)}\n"
		if removed_hosts:
			for host in removed_hosts:
				telegram_message += f"\n{emoji_check} {host[0]}"
		telegram_message += f"\n\nTOTAL HOSTS: {len(total_hosts)}"
		if len(telegram_message) > 1024:
			telegram_message = f"{emoji_alert} {inventory_name} {emoji_alert}\n\n{emoji_clock} Alert sent: {strftime("%c")}\n\n"
			telegram_message += f"{emoji_pencil} Added Hosts: {len(added_hosts)}\n"
			telegram_message += f"\n\n{emoji_pencil} Removed Hosts: {len(removed_hosts)}\n"
			telegram_message += f"\n\nTOTAL HOSTS: {len(total_hosts)}"
		return telegram_message.encode("utf-8")


	def create_log_by_telegram_code(self, response_http_code: int, name: str) -> None:
		"""
		Method that generates an application log based on the HTTP response code of the Telegram API.

		Parameters:
			response_http_code (int): HTTP code returned by the Telegram API.
			name (str): Inventory's name.
		"""
		match response_http_code:
			case 200:
				self.logger.create_log("Telegram message sent", 2, f"_{name}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 400:
				self.logger.create_log("Telegram message not sent. Bad request.", 4, f"_{name}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 401:
				self.logger.create_log("Telegram message not sent. Unauthorized.", 4, f"_{name}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
			case 404:
				self.logger.create_log("Telegram message not sent. Not found.", 4, f"_{name}", use_stream_handler = True, use_file_handler = True, file_name = self.constants.LOG_FILE, user = self.constants.USER, group = self.constants.GROUP)
