from abc import abstractmethod

class BookApi(object):

	def __init__(self, baseUrl, apiKey):
		self.baseUrl = baseUrl
		self.apiKey = apiKey

	@abstractmethod
	def get_bookdetail(self, isbncode):
		pass

	# Parse data of the request into a uniform JSON book data structure
	@abstractmethod
	def parse(self, data):
		pass

	def getbook(self, isbn):
		resp = self.get_bookdetail(isbn)
		book = self.parse(resp)

		return book