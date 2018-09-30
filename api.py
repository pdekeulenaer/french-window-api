from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
import models
import database

app = Flask(__name__)
api = Api(app)


def resource_not_found():
	abort(404, message="Requested resource does not exist")

class BookList(Resource):

	def books(self):
		return models.Book.query.all()

	def get(self):
		return map(lambda l: l.as_dict(), self.books())


	def post(self):
		if not request.json or 'title' not in request.json:
			abort(400)

		book = models.Book()
		book.title = request.json['title']
		book.description = request.json.get('description','')

		database.db.session.add(book)
		database.db.session.commit()

		return book.as_dict(), 201

class Book(Resource):

	def get(self, book_id):
		book = models.Book.query.filter(models.Book.id==book_id).first();
		if book is None:
			resource_not_found()

		return book.as_dict()




api.add_resource(BookList, '/books/')
api.add_resource(Book, '/books/<int:book_id>')

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