from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from database import db
import datetime

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


class Author(db.Model):
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False) 
	books = relationship('Book')

class User(db.Model):
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	email = Column(String, nullable=False)

	# Currently set to max 1 library per user
	library = relationship('Library', uselist=False)

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
