phonos
======

Telephone Number Inventory Database

Running Phonos
--------------

Run Phonos using the command `gunicorn phonos:app`

You should then be able to access it at the following URL: `http://localhost:8000`

Settings
--------

Phonos requires a database that supports the JSON datatype.  To point Phonos to a database create a config file named `phonos.cfg` that looks something like this:

    SQLALCHEMY_DATABASE_URI = "postgresql://user:password@db_host/db_name"

If you create it in a directory other than this one, you can specify the path to the file using the `PHONOS_CONFIG` environment variable.
