from os import scandir
from threading import Thread
from modules.UtilsClass import Utils
from modules.ElasticClass import Elastic

"""
Class that allows you to manage everything related to
inventories.
"""
class Inventories:
	"""
	Property that stores an object of type Utils.
	"""
	utils = None

	"""
	Property that stores an object of type Elastic.
	"""
	elastic = None

	"""
	Property that stores the assigned data in the Inv-Alert
	configuration file.
	"""
	inv_alert_conf = None

	"""
	Property that stores the path where inventories are
	stored.
	"""
	path_inventories = None

	"""
	Constructor for the Inventories class.

	Parameters:
	self -- An instantiated object of the Inventories class.
	"""
	def __init__(self):
		self.utils = Utils()
		self.inv_alert_conf = self.utils.readYamlFile(self.utils.getPathInvAlert('conf') + '/inv_alert_conf.yaml', 'r')
		self.path_inventories = self.utils.getPathInvAlert(self.inv_alert_conf['inv_folder'])
		self.elastic = Elastic(self.inv_alert_conf)
	
	"""
	"""
	def loadAllInventories(self):
		try:
			if float(self.inv_alert_conf['es_version']) < 7.0 or float(self.inv_alert_conf['es_version']) > 7.13:
				print("\nElasticSearch version not supported by Inv-Alert.")
			else:
				print("Inv-Alert v3.0")
				print("@2021 Tekium. All rights reserved.")
				print("Author: Erick Rodriguez")
				print("Email: erickrr.tbd93@gmail.com, erodriguez@tekium.mx")
				print("License: GPLv3")
				print("\nInv-Alert started...")
				conn_es = self.elastic.getConnectionElastic()
				list_all_inventories = self.getListInventories()
				if len(list_all_inventories) == 0:
					self.utils.createInvAlertLog("No inventories were found in: " + self.path_inventories, 2)
					print("\nNo inventories were found in: " + self.path_inventories)
				else:
					print("\nINVENTORIES:")
					print("Inventory folder: " + self.path_inventories)
					print("Total inventories found: " + str(len(list_all_inventories)))
					for inventory in list_all_inventories:
						print(inventory + " loaded and executed.")
						inventory_yaml = self.utils.readYamlFile(self.path_inventories + '/' + inventory + '/' + inventory + '.yaml', 'r')
						thread_inventory = Thread(target = self.elastic.getInventory, args = (inventory_yaml, conn_es, )).start()
		except KeyError as exception:
			print("Error")

	"""
	Method that obtains a list with all the inventories
	created.

	Parameters:
	self -- An instantiated object of the Inventories class.

	Return:
	sub_directories -- List with all inventories found.

	Exceptions:
	OSError -- This exception is raised when a system function
	           returns a system-related error, including I/O
	           failures such as “file not found” or “disk full”
	           (not for illegal argument types or other incidental
	           errors).
	"""
	def getListInventories(self):
		try:
			with scandir(self.path_inventories) as directories:
				sub_directories = [directory.name for directory in directories if directory.is_dir()]
		except OSError as exception:
			self.utils.createInvAlertLog(exception, 3)
			print("\nError getting inventories. For more information, see the logs.")
		else:
			return sub_directories