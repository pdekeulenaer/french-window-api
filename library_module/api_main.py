from flask import g, Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort
from flask_httpauth import HTTPBasicAuth

from fuzzywuzzy import fuzz, process
from book_api import search
import json

import models
import database
import controller

auth = HTTPBasicAuth()

# Verifies the password or token from a user. Returns True if user is authorized. used by HTTPAuh package
@auth.verify_password
def verify_password(user_token, pw):

	user = models.User.verify_token(user_token)
	if user is None:
		user = models.User.query.filter_by(name = user_token).first()
		if not user or not user.verify_password(pw):
			return False

	#Set user in global object
	g.user = user
	return True


def resource_not_found():
	abort(404, message="Requested resource does not exist")


class Library(Resource):

	# create a new book and automatically add it to this users' library
	@auth.login_required
	def post(self):
		if not request.json or 'title' not in request.json:
			abort(400)

		ctrl = controller.UserController(g.user)
		book = ctrl.add(request.json)
		ctrl.commit()

		return book.as_dict(), 201

	# Pass it a JSON GET request with 'title' to search for a title
	# return will be a list of books in authenticated user's collection
	# If no JSON request or title in request, full collection will be returned
	@auth.login_required
	def get(self):
		if not request.json or 'title' not in request.json:
			self.collection()

		matchTitle = request.json['title']
		# Look for similar titles
		ctrl = controller.UserController(g.user)
		books = ctrl.collection()
		matches = filter(lambda l: (fuzz.token_set_ratio(l.title, matchTitle) > 80), books)
		return map(lambda l: l.as_dict_verbose(), matches)

	def collection(self):
		return map(lambda l: l.as_dict_verbose(), g.user.library.books())


#Needs to be reviewed
class BookDetail(Resource):

	def get(self, book_id=None, querystr=''):

		if 'isbn10' in request.args.keys():
			return self.get_isbn(isbn10=request.args['isbn10'])

		if 'isbn13' in request.args.keys():
			return self.get_isbn(isbn13=request.args['isbn13'])

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


class Series(Resource):
	# return the top 50 series that satisfy the keyword
	def get(self, searchStr=""):
		series = models.Series.query.filter(models.Series.name.like('%{0}%'.format(searchStr))).limit(50).all()
		return jsonify(map(lambda l: l.as_dict(), series))

class Search(Resource):
	@auth.login_required
	def get(self, isbn=None):
		if isbn is None:
			resource_not_found()

		print isbn

		# calls method in book_api classes
		book = search(isbn)
		if book is None:
			return {}

		assert type(book) is dict
		return book


class Author(Resource):
	def get(self, author_id=None):
		#Return list of authors if no ID is specified
		if author_id is None:
			return map(lambda l: l.as_dict(), models.Author.query.all())

		author = models.Author.query.filter(models.Author.id==author_id).first()
		
		if author is None:
			resource_not_found()
		
		return author.as_dict()




class Authentication(Resource):
	@auth.login_required
	def get(self):
		return {'message' : 'Hello there!', 'name' : g.user.name }

class AuthenticationToken(Resource):
	@auth.login_required
	def get(self):
		print request.headers
		print request.json
		token = g.user.generate_token()
		return jsonify({'token':token.decode('ascii')})

class Statistics(Resource):
	@auth.login_required
	def get(self):
		control = controller.UserController(g.user)
		data = {
			'Books' : control.nbooks(),
			'Authors' : control.nauthors(),
			'Series' : control.nseries()
		}
		return jsonify(data)

# classic style routing
# @app.route('/auth/generate_token')
# @auth.login_required
# def get_auth_token():
# 	print request.headers
# 	print request.json
# 	token = g.user.generate_token()
# 	return jsonify({'token':token.decode('ascii')})

def build_api(app):
	api = Api(app)

	api.add_resource(Authentication, '/api/auth/')
	api.add_resource(AuthenticationToken, '/api/auth/generate_token')
	api.add_resource(Library, '/api/library/')
	api.add_resource(Author, '/api/authors/', '/api/authors/<int:author_id>')
	api.add_resource(BookDetail, '/api/books/', '/api/books/<int:book_id>')
	api.add_resource(Statistics, '/api/stats/')
	api.add_resource(Series, '/api/series/', '/api/series/<string:searchStr>')
	api.add_resource(Search, '/api/search/<string:isbn>')

