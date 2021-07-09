

class Configuration:
	"""
	Property that stores an object of type FormDialogs.
	"""
	form_dialog = None

	"""
	Constructor for the Configuration class.

	Parameters:
	self -- An instantiated object of the Configuration class.
	"""
	def __init__(self, form_dialog):
		self.form_dialog = form_dialog

	def createConfiguration(self):
		data_conf = []
		version_es = self.form_dialog.getDataNumberDecimal("Enter the ElasticSearch version:", "7.13")
		host_es = self.form_dialog.getDataIP("Enter the ElasticSearch IP address:", "localhost")
		port_es = self.form_dialog.getDataPort("Enter the ElasticSearch listening port:", "9200")
		folder_inv = self.form_dialog.getDataNameFolderOrFile("Enter the name of the folder where the alert rules will be hosted:", "folder_inv")
		use_ssl = self.form_dialog.getDataYesOrNo("\nDo you want Telk-Alert to connect to ElasticSearch using the SSL/TLS protocol?", "Connection Via SSL/TLS")
		data_conf.append(version_es)
		data_conf.append(host_es)
		data_conf.append(port_es)
		data_conf.append(folder_inv)
		print(data_conf)
		self.form_dialog.mainMenu()