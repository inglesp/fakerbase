test: test-fakerbase tests-with-fakerbase tests-without-fakerbase

test-fakerbase:
	DJANGO_SETTINGS_MODULE=tests.settings ./manage.py test fakerbase
	
tests-with-fakerbase:
	DJANGO_SETTINGS_MODULE=tests.settings_with_fakerbase ./manage.py test tests

tests-without-fakerbase:
	DJANGO_SETTINGS_MODULE=tests.settings ./manage.py test tests

