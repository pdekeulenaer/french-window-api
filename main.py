from flask import Flask

import models
import database

app = Flask(__name__)

@app.route('/')
def hello():
	return 'Hello world!'

def configapp() :
	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	database.db.init_app(app)
	app.app_context().push()

	database.db.create_all()
	
if __name__ == '__main__':
	configapp()
	app.run()