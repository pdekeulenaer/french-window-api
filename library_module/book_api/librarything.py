from api import BookApi

import requests, untangle, urlparse

class LibraryThingApi(BookApi):


	def __init__(self):
		baseUrl = "http://www.librarything.com/services/rest/1.1/?method=librarything.ck.getwork&isbn={0}&apikey={1}"
		apiKey = '5c66e319120510ab582211c16364ca3d'
		
		self.coverUrl = "https://www.librarything.com/devkey/{0}/medium/isbn/{1}"

		super(LibraryThingApi, self).__init__(baseUrl,apiKey)

	def get_bookdetail(self, isbncode):
		resp = requests.get(self.baseUrl.format(isbncode, self.apiKey))
		return resp

	# passing 1 or multiple results - selecting the first
	def parse(self, response, isbncode=None):

		if isbncode is None:
			isbncode = urlparse.parse_qs(response.url)['isbn'][0]

		dataobj = untangle.parse(response.content)

		if dataobj.response['stat'] == 'fail':
			return None

		work = dataobj.response.ltml.item

		book = {}

		book['title'] = work.title.cdata
		book['author'] = work.author.cdata
		book['isbn'] = isbncode

		book['pagecount'] = None
		book['cover'] = self.coverUrl.format(self.apiKey, isbncode)
		book['publisher'] = None
		book['publishedDate'] = None
		book['description'] = None

		return book
