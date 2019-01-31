from api import BookApi

import requests, json, urlparse

class GoogleApi(BookApi):


	def __init__(self):
		baseUrl = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
		apiKey = ''
		
		super(GoogleApi, self).__init__(baseUrl,apiKey)

	def get_bookdetail(self, isbncode):
		resp = requests.get(self.baseUrl + isbncode)
		return resp


	# passing 1 or multiple results - selecting the first
	def parse(self, response, isbncode = None):
		data = response.json()

		if data['totalItems'] == 0:
			return None

		volume = data['items'][0]['volumeInfo']

		book = {}

		book['title'] = volume.get('title')
		book['publisher'] = volume.get('publisher')
		book['publishedDate'] = volume.get('publishedDate')
		book['description'] = volume.get('description')

		book['author'] = None
		if (volume.get('authors') is not None):
			book['author'] = volume.get('authors')[0]
		
		book['pagecount'] = volume.get('pageCount')
		book['cover'] = volume.get('imageLinks').get('thumbnail')

		book['isbn'] = volume.get('industryIdentifiers')[-1]['identifier']

		return book
