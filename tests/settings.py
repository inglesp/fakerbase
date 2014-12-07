INSTALLED_APPS = [
    'tests',
    'fakerbase',
]

# The following are required by Django to run the tests. {
SECRET_KEY = '?'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

MIDDLEWARE_CLASSES = []
# }

