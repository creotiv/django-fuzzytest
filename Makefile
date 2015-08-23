.PHONY: test

test:
	DJANGO_SETTINGS_MODULE=tests.settings \
		django-admin.py test tests

