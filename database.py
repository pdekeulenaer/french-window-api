from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# TYPE = config.DB_TYPE

# def generate_engine():
# 	if TYPE == 'sqlite':
# 		db_str = sqlite_str()
# 	else:
# 		db_str = mysql_str()
# 	engine = create_engine(db_str)
# 	engine.raw_connection().connection.text_factory = str
# 	return engine

# def _build():
# 	import models
# 	Base.metadata.create_all(generate_engine())	

# def sqlite_str():
# 	return 'sqlite:///askhenry_2.db'

# def mysql_str():
# 	host = 'pdekeulenaer.mysql.pythonanywhere-services.com'
# 	username = 'pdekeulenaer'
# 	password = 'meghana8'
# 	dbname = 'pdekeulenaer$askhenry'
# 	mysql_string = 'mysql+mysqldb://%s:%s@%s/%s' % (username, password, host, dbname)
# 	return mysql_string	