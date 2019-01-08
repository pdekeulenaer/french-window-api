from flask import g, Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user

import models
import database
import controller

app = Flask(__name__)
login_manager = LoginManager()


@app.route('/')
def index():
	return redirect(url_for('mybooks'))


class BookViews:
	@app.route('/book/<book_id>')
	def bookview(book_id):
		book = controller.BookController.get(book_id)
		return render_template('books/detail.html', book=book)


class LibraryViews:

	@app.route('/library/')
	@login_required
	def mybooks():

		ctrl = controller.UserController(current_user)
		books = ctrl.collection()
		return render_template('library/collection.html', pagename='Booklist', books=books)

	@app.route('/library/add/', methods=['GET'])
	@login_required
	def add_get():
		return render_template('library/add.html', pagename='Add a new book')

	@app.route('/library/add/', methods=['POST'])
	@login_required
	def add_post():
		ctrl = controller.UserController(current_user)
		ctrl.add(request.form.to_dict())
		ctrl.commit()
		return redirect(url_for('mybooks'))

	# API toggles

	@app.route('/library/disactivate/')
	@login_required
	def disactivate():
		book_id = request.args.get('book_id')
		ctrl = controller.UserController(current_user)
		ctrl.disactivate(book_id)
		ctrl.commit()
		return redirect(url_for('mybooks'))

	@app.route('/library/reactivate/')
	@login_required
	def reactivate():
		book_id = request.args.get('book_id')
		ctrl = controller.UserController(current_user)
		ctrl.reactivate(book_id)
		ctrl.commit()
		return redirect(url_for('mybooks'))

	@app.route('/library/read/')
	@login_required
	def mark_read():
		book_id = request.args.get('book_id')
		ctrl = controller.UserController(current_user)
		ctrl.mark_read(book_id)
		ctrl.commit()

		return redirect(url_for('mybooks'))

	@app.route('/library/unread/')
	@login_required
	def mark_unread():
		book_id = request.args.get('book_id')
		ctrl = controller.UserController(current_user)
		ctrl.mark_unread(book_id)
		ctrl.commit()

		return redirect(url_for('mybooks'))


class Authentication:
	@app.route('/user/login', methods=['GET'])
	def login():
		return render_template('user/login.html', pagename='Login')	
	
	@app.route('/user/login', methods=['POST'])
	def validate():
		user = request.form['username']
		pw = request.form['pwd']

		user = models.User.query.filter_by(name = user).first()
		if user is None:
			return redirect('user/login')

		if not user.verify_password(pw):
			return redirect('user/login')

		control = controller.UserController(user)
		login_user(user)

		return redirect(url_for('mybooks'))
	
	@app.route('/user/logout')
	def logout():
		logout_user()
		return redirect('user/login')

@login_manager.user_loader
def load_user(user_id):
	return controller.UserController.get(user_id)

def configapp() :
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devtest3.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['SECRET_KEY'] = "my name is philip de keulenaer and this is my secret"

	database.db.init_app(app)
	app.app_context().push()
	database.db.create_all()

	login_manager.init_app(app)
	login_manager.login_view = 'login'
	

if __name__ == '__main__':
	configapp()
	app.run(debug=True)
