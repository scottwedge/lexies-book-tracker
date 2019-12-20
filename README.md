# read

just the faves
show everything

# reading

# to read

i own a copy
recommended to me
recommended by a friend
looks interesting

## Getting started

Clone the repo, install dependencies, set up the database.

```
flask db upgrade
```

```pycon
>>> from src import db, models
>>> user = models.User(username="alexwlchan")
>>> import getpass
>>> user.set_password(password=PASSWORD)
>>> db.session.add(user)
>>> db.session.commit()
```