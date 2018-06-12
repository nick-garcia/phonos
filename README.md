phonos
======

Telephone Number Inventory Database

Running Phonos
--------------

Run Phonos using the command `gunicorn phonos:app`

You should then be able to access it at the following URL: `http://localhost:8000`

Settings
--------

By default Phonos is set up to use an in-memory SQLite database.  In order to configure it to use a more permanent database, create a config file named `phonos.cfg` that looks something like this:

    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@db_host/db_name"

If you create it in a directory other than this one, you can specify the path to the file using the `PHONOS_CONFIG` environment variable.
