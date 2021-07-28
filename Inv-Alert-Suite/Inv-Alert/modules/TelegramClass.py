from pycurl import Curl, RESPONSE_CODE

def Telegram:
	"""
	"""
	sendType = { 'document' : 'sendDocument' }

	def uploadFileTelegram(self, url, method, options):
		c = Curl()
		storage = StringIO()
		c.setopt(c.URL, url + method)
		c.setopt(c.HTTPPOST, options)
		c.perform_rs()
		return c.getinfo(RESPONSE_CODE)

	def sendTelegramAlert(self, chat_id, bot_token, message):
		print("Hola")