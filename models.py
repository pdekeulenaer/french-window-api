from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime, Boolean
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from flask import current_app as app

from flask_login import UserMixin

from database import db
import datetime
import hashlib

from sqlalchemy.orm import relationship

class Book(db.Model):
	id = Column(Integer, primary_key=True)
	title = Column(String(255), nullable=False)

	# primary information
	description = Column(Text, nullable=True)
	isbn13 = Column(String(255), nullable=True)
	isbn10 = Column(String(255), nullable=True)
	publisher = Column(String(255), nullable=True)

	# secondary inputs
	release_date = Column(String, nullable=True)
	pagecount = Column(Integer, nullable=True)
	bindingtype = Column(String, nullable=True)
	genre = Column(String(255), nullable=True)
	image_path = Column(String(255), default='no_image_available.gif')


	# links to other fields
	author_id = Column(Integer, ForeignKey('author.id'))
	author = relationship('Author')

	series_id = Column(Integer, ForeignKey('series.id'), nullable=True)
	series_nr = Column(Integer, default=0)
	series = relationship('Series')

	# includes user scoring
	libraries = relationship('AssociationBookLibrary')

	# link to genre tags
	tags = relationship('AssociationBookTags', back_populates='book')


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


	def __str__(self):
		return self.title


class Series(db.Model):
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	sequence = Column(Integer, default=0)
	books = relationship('Book')


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

class User(db.Model, UserMixin):
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
		booklist = []
		for assoc in filter(lambda l: l.active, self.associations):
			if assoc.active:
				b = assoc.book
				b.read = assoc.read
				b.rating = assoc.rating
				booklist.append(b)
		return booklist
		# return map(lambda l: l.book, self.associations)


class AssociationBookLibrary(db.Model):
	library_id = Column(Integer, ForeignKey('library.id'), primary_key=True)
	book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)
	date_added = Column(DateTime, default=datetime.datetime.utcnow)

	# specific user-provided data
	rating = Column(Integer, nullable=True)
	read = Column(Integer, default=0.0)

	# active book?
	active = Column(Boolean, default=True)
	
	# connections to others
	library = relationship('Library', back_populates='associations')
	book = relationship('Book')

class AssociationBookTags(db.Model):
	tag_id = Column(Integer, ForeignKey('tag.id'), primary_key=True)
	book_id = Column(Integer, ForeignKey('book.id'), primary_key=True)

	book = relationship('Book', back_populates='tags')
	tag = relationship('Tag')

class Tag(db.Model):
	id = Column(Integer, primary_key=True)
	tag = Column(String(255), nullable=False)

	@staticmethod
	def search(label):
		tag = Tag.query.filter_by(tag=label).first()
		if tag is not None:
			return tag
		return None

	# Check if tag exists, if not create a new author
	@staticmethod
	def default(label):
		tag = Tag.search(name)
		if tag is None:
			# Author is not known
			tag = Tag(tag=label)
			db.session.add(tag)
			db.session.commit()

		return tag