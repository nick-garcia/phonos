import sys
try:
    exec("f'fstring test'")
except SyntaxError:
    print("Phonos requires at least Python 3.5.")
    sys.exit(1)

try:
    import baker
except ImportError:
    print("You must first install the requirements with 'pip install -r requirements.txt'")
    sys.exit(1)

import phonos.model
from gunicorn.app.wsgiapp import WSGIApplication

@baker.command
def initdb():
    """ Reinitialize the database.

    This will drop all existing tables, create new tables, populate the countries table, and create the default admin user.
    """
    phonos.model.initialize()
    print("Database initialized!")

baker.run()
