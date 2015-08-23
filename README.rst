==============================
Django Fuzzy Test
==============================

This is the automatic Fuzzy Test tool for testing Django applications.
It generates url and params map based on your activity on dev server and then use it to fuzzy test your application.

How to use
^^^^^^^^^^

Add to installed applications
    INSTALLED_APPS += ('django_fuzzytest',)

Run fuzzyserver to collect url and params cache:
    python manage.py fuzzyserver --cache=.fuzzycache

After data was collected you can start testing:
    python manage.py fuzzytest --cache=.fuzzycache

Here's a screenshot of the panel in action:

.. image:: https://raw.github.com/creotiv/django-fuzzytest/master/example.png
   :width: 1214
   :height: 747



