import main, controller, models, database

main.configapp()

# Replace wit controller methods
def buildObjects(db):
	u1 = models.User(name="Meghana", email="megmeg@meg.meg")
	u1.set_password('admin')

	a1 = models.Author(name='John Williams')
	b1 = models.Book(title="Once upon a time", description="Great book")
	b2 = models.Book(title="Second upon a time", description="Another classic")
	
	l = models.Library()

	b1.author = a1
	b2.author = a1

	l.user = u1

	assoc = models.AssociationBookLibrary(library=l)
	assoc.book = b2

	db.session.add(a1)
	db.session.add(b1)
	db.session.add(b2)
	db.session.add(u1)
	db.session.add(l)
	db.session.commit()

buildObjects(database.db)


user = models.User.query.filter_by(name = 'Meghana').first()

badblood = {'author': 'John Carreyrou', 
			'title':'Bad Blood',
			'publisher':'Picador', 
			'description':'Lies in a sillicon valley startup', 
			'isbn13':'9781509868070',
			'bindingtype':'paperback',
			'pagecount':'338', 
			'genre':'non-fiction'
			}


# ctrl = controller.UserController(user)
# ctrl.add(badblood)

# ctrl.commit()

ctrl = controller.SeriesController()

res = ctrl.search('Wheel of Time')
print res

ctrl.setdefault('Wheel of Time')