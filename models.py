from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from flask import current_app as app

from database import db
import datetime
import hashlib

from sqlalchemy.orm import relationship

class Book(db.Model):
	id = Column(Integer, primary_key=True)
	title = Column(String(255), nullable=False)

	description = Column(Text, nullable=True)
	isbn13 = Column(String(255), nullable=True)
	isbn10 = Column(String(255), nullable=True)
	publisher = Column(String(255), nullable=True)

	author_id = Column(Integer, ForeignKey('author.id'))
	author = relationship('Author')

	libraries = relationship('AssociationBookLibrary')

	def as_dict(self):
		return {col.name: getattr(self, col.name) for col in self.__table__.columns}	

	def as_dict_verbose(self):
		d = self.as_dict()
		d.pop('author_id')
		d['author'] = self.author.as_dict()
		return d

	def parse(self, d):
		self.isbn13 = d.get('isbn13')
		self.isbn10 = d.get('isbn10')
		self.description = d.get('description')
		self.publisher = d.get('publisher')
		self.parse_author(d.get('author', None))

	def parse_author(self, d):
		#check if an author exists
		if d is None:
			self.author = Author.unknown_author()
			return	

		if ('id' in d): 		author = Author.query.get(d['id'])
		elif ('name' in d): 	author = Author.default(d['name'])
		else: 					author = None

		if author is None: 		author = Author.unknown_author()
		self.author = author


class Author(db.Model):
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False) 
	books = relationship('Book')

	@staticmethod
	def search(name):
		author = Author.query.filter_by(name=name).first()
		if author is not None:
			return author
		return None

	# staticn method to return instance of unknown author - TOTO optimize to singleton
	@staticmethod
	def unknown_author():
		return Author.default('Unknown Author')

	# Check if author exists, if not create a new author
	@staticmethod
	def default(name):
		author = Author.search(name)
		if author is None:
			# Author is not known
			author = Author(name=name)
			db.session.add(author)
			db.session.commit()

		return author
			

	def as_dict(self):
		return {col.name: getattr(self, col.name) for col in self.__table__.columns}

class User(db.Model):
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	email = Column(String, nullable=False)
	password_hash = Column(String, nullable=False)

	# Currently set to max 1 library per user
	library = relationship('Library', uselist=False)

	def verify_password(self, value):
		return self.hash(value) == self.password_hash;

	# this should be private - TODO abstract into util class
	def hash(self, value):
		return hashlib.sha256(value).hexdigest()

	def set_password(self, value):
		self.password_hash = self.hash(value)

	# authentication token
	def generate_token(self, expiration=300):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	# verify an authentication token
	@staticmethod
	def verify_token(token):
		s = Serializer(app.config['SECRET_KEY'])

		try: 
			data = s.loads(token)
		except SignatureExpired:
			return None
		except BadSignature:
			return None

		user = User.query.get(data['id'])
		return user



class Library(db.Model):
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	date_created = Column(DateTime, default=datetime.datetime.utcnow)

	user = relationship('User', back_populates='library')
	associations = relationship('AssociationBookLibrary', back_populates='library')

	# Get all books in this library
	def books(self):
		return map(lambda l: l.book, self.associations)

	# Add a book to the library - create association boject 
	def addbook(self, book):
		if (book not in self.books()):
			assoc = AssociationBookLibrary(library=self)
			assoc.book = book

class AssociationBookLibrary(db.Model):
	library_id = Column(Integer, ForeignKey('library.id'), primary_key=True)
	book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
	date_added = Column(DateTime, default=datetime.datetime.utcnow)
	
	library = relationship('Library', back_populates='associations')
	book = relationship('Book')


def buildObjects(db):
	a1 = Author(name='John Williams')
	b1 = Book(title="Once upon a time", description="Great book")
	b2 = Book(title="Second upon a time", description="Another classic")
	u1 = User(name="Meghana", email="megmeg@meg.meg")
	l = Library()

	u1.set_password('admin')

	b1.author = a1
	b2.author = a1

	l.user = u1

	assoc = AssociationBookLibrary(library=l)
	assoc.book = b2

	db.session.add(a1)
	db.session.add(b1)
	db.session.add(b2)
	db.session.add(u1)
	db.session.add(l)
	db.session.commit()
