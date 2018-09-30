from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import models
import database

app = Flask(__name__)
api = Api(app)


def resource_not_found():
	abort(404, message="Requested resource does not exist")

class Book(Resource):

	def books(self):
		return models.Book.query.all()

	def post(self):
		if not request.json or 'title' not in request.json:
			abort(400)

		book = models.Book()
		book.title = request.json['title']
		book.description = request.json.get('description','')

		database.db.session.add(book)
		database.db.session.commit()

		return book.as_dict(), 201

	def get(self, book_id=None, querystr=''):

		if 'isbn10' in request.args.keys():
			return self.get_isbn(isbn10=request.args['isbn10'])

		if 'isbn13' in request.args.keys():
			return self.get_isbn(isbn13=request.args['isbn13'])

		if book_id is None:
			return map(lambda l: l.as_dict(), self.books())

		book = models.Book.query.filter(models.Book.id==book_id).first();
		if book is None:
			resource_not_found()

		return book.as_dict()


	def get_isbn(self, isbn10=None, isbn13=None):
		bookquery = models.Book.query
		book = None
		if isbn10 is not None:
			book = bookquery.filter(models.Book.isbn10==isbn10).first()

		if book is None and isbn13 is not None:
			book = bookquery.filter(models.Book.isbn13==isbn13).first()

		if book is None: resource_not_found()

		return book.as_dict()

class Author(Resource):
	def get(self, author_id=None):
		#Return list of authors if no ID is specified
		if author_id is None:
			return map(lambda l: l.as_dict(), models.Author.query.all())

		author = models.Author.query.filter(models.Author.id==author_id).first()
		
		if author is None:
			resource_not_found()
		
		return author.as_dict()



api.add_resource(Book, '/books/', '/books/<int:book_id>')
api.add_resource(Author, '/authors/', '/authors/<int:author_id>')

# @app.route('/')
# def hello():
# 	return 'Hello world!'

def configapp() :
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	database.db.init_app(app)
	app.app_context().push()
	database.db.create_all()
	

if __name__ == '__main__':
	configapp()
	app.run(debug=True)