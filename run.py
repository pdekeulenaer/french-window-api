from flask import Flask

from library_module import app

if __name__ == '__main__':
	app.run(debug=app.config["DEBUG"])