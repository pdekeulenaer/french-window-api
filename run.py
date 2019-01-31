from flask import Flask

from library_module import app

app.run(debug=app.config["DEBUG"])