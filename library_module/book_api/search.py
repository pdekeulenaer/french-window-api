from google import GoogleApi
from librarything import LibraryThingApi


# create the APIs
google = GoogleApi()
librarything = LibraryThingApi()

apis = [google, librarything]

# search books
# cycles through available APIs
def search(isbn):

	for api in apis:
		book = api.getbook(isbn)
		if book is not None:
			return book

	return None
