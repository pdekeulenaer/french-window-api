import models, database
import datetime, hashlib, urllib

class Controller:
	model = None

	def __init__(self):
		self.session = database.db.session

	def setuser(self, user):
		self.user = user

	def commit(self):
		self.session.commit()

	def search(self, name):
		obj = self.model.query.filter_by(name=name).first()
		return obj

	def setdefault(self, name):
		obj = self.search(name)
		if obj is None:
			obj = self.add(name)
			self.commit()

		return obj

class BookController(Controller):
	
	# Bookdata structured as a dictionary
	def add(self, bookdata):
	
		book = models.Book()
		book = self.parse(book, bookdata)

		# check if author is real
		author = self.detect_author(bookdata['author'])
		book.author = author

		# check if series is real
		if bookdata.setdefault('series_name') is not None:
			ctrl = SeriesController()
			series = ctrl.setdefault(bookdata['series_name'])

			book.series = series
			book.series_nr = bookdata.setdefault('series_nr')

		self.session.add(book)

		return book		

	def parse(self, book, bookdata):

		book.title = bookdata.setdefault('title')
		book.isbn10 = bookdata.setdefault('isbn10')
		book.isbn13 = bookdata.setdefault('isbn13')
		book.publisher = bookdata.setdefault('publisher')
		book.description = bookdata.setdefault('description')
		
		#assuming this is YYYY-MM-DD

		# def reldate(release_date):
		# 	if release_date is not None:
				
		# 		els = map(lambda l: int(l), release_date.split('-'))
		# 		print els
		# 		if len(els) == 1:
		# 			return datetime.datetime(els[0], 1, 1)
		# 		elif len(els) == 2:
		# 			return datetime.datetime(els[0], els[1], 1)
		# 		elif (len(els) >= 3):
		# 			return datetime.datetime(els[0], els[1], els[2])
		# 		else:
		# 			return None
		# 	return None
		# book.release_date = reldate(bookdata.setdefault('release_date'))
		book.release_date = bookdata.setdefault('release_date')
		book.pagecount = bookdata.setdefault('pagecount')
		book.bindingtype = bookdata.setdefault('bindingtype')
		book.genre = bookdata.setdefault('genre')

		# Book image 
		# TODO - refactor this
		image_path = bookdata.setdefault('image_path')
		print "[Controller BookController.parse()]"
		print image_path
		if image_path is None or image_path == "":
			book.image_path = None
		else:
			# save image locally
			hasher = hashlib.new('sha256')
			hasher.update(book.title)
			fileloc = book.title + "_" + hasher.hexdigest() + ".jpg"
			urllib.urlretrieve(image_path, 'static/img/'+fileloc)
			book.image_path = fileloc
		return book


	def detect_author(self, authorobj):
		#check if an author exists
		if authorobj is None:
			author = models.Author.unknown_author()
			return author	

		if type(authorobj) is dict:
			if ('id' in authorobj): 		author = models.Author.query.get(authorobj['id'])
			elif ('name' in authorobj): 	author = models.Author.default(authorobj['name'])
			else: 							author = models.Author.unknown_author()
		else: 					
			author = models.Author.default(authorobj)

		if author is None:
			author = models.Author.unknown_author()
		
		return author

	def tagbook(self, book, taglabel):
		t = models.Tag.default(taglabel)
		assoc = models.AssociationBookTags(tag=t, book=book)
		return True

	@staticmethod
	def get(book_id):
		return models.Book.query.filter_by(id=book_id).first()


class UserController(Controller):
	def __init__(self, user):
		# TODO fix this with super override
		self.session = database.db.session
		self.user = user
		self._setlib()

	def _setlib(self):
		# open library controller
		self.library_control = LibraryController()
		self.library_control.setlib(self.user.library)


	def add(self, bookdata):
		# create new book in ssytem
		bookctrl = BookController()
		book = bookctrl.add(bookdata)

		# add book to current library
		self.library_control.collect(book)

		# Check if book was read
		has_read = (bookdata.setdefault("has_read",False))
		print "[Controller UserController.add()]"
		print has_read
		print type(has_read)

		if (has_read):
			self.mark_read(book.id)

		return book

	def mark_read(self, book_id):
		# book = BookController.get(book_id)
		self.library_control.markread(book_id)

	def mark_unread(self, book_id):
		# book = BookController.get(book_id)
		self.library_control.markunread(book_id)

	def collection(self):
		return self.user.library.books()

	def disactivate(self, book_id):
		self.library_control.remove(book_id)

	def reactivate(self, book_id):
		self.library_control.reactivate(book_id)

	@staticmethod
	def get(user_id):
		return models.User.query.filter_by(id=user_id).first()

class SeriesController(Controller):
	model = models.Series

	def add(self, name):
		obj = models.Series(name=name)
		self.session.add(obj)

		return obj

class LibraryController(Controller):
	def setlib(self, library):
		self.library = library

	def collect(self, book):
		if (book not in self.library.books()):
			assoc = models.AssociationBookLibrary(library=self.library, book=book)

	def getassoc(self, book_id):
		assoc = models.AssociationBookLibrary.query.filter_by(book_id=book_id, library_id=self.library.id).first()
		return assoc

	def markread(self, book_id):
		assoc = self.getassoc(book_id)
		assoc.read = 1

	def markunread(self, book_id):
		assoc = self.getassoc(book_id)
		assoc.read = 0

	def remove(self, book_id):
		assoc = self.getassoc(book_id)
		assoc.active = False

	def reactivate(self, book_id):
		assoc = self.getassoc(book_id)
		assoc.active = True
		
