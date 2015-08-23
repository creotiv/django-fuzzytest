# coding: utf-8
from __future__ import unicode_literals
import functools
import re
from optparse import make_option
import traceback

from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model
from django.utils.translation import activate

from .utils import UrlFinder, RegexpInverter

class FuzzyRunner(object):

    TYPES = {
        'int':r'[\d]',
        'string':r'[a-z0-9\!\"\#\$\%\&\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\'\^\_\`\{\|\}\~]',
        'utf': r'[йцукенгшщзхъфывапролджэячсмитьбю]'
    }

    def __init__(self, urls_info):
        self.urls_info = urls_info
        self.user = None
        self.ir = RegexpInverter()

    def run(self):
        self.user = get_user_model().objects.create_user(
            'fuzzy', 
            'fuzzy@localhost.com', 
            'fuzzytest'
        )
        self.admin = get_user_model().objects.create_superuser(
            'fuzzyadmin', 
            'fuzzyadmin@localhost.com', 
            'fuzzytest'
        )
        try:
            client = Client()
            # BugFix https://github.com/nsupdate-info/nsupdate.info/issues/206
            activate('en')
            # anonymous user test
            print "####################################"
            print "## ANONYMOUS USER ##################"
            print "####################################"
            self._run_tests(client)

            # authorised user test
            print "####################################"
            print "## AUTHORISED USER #################"
            print "####################################"
            login = functools.partial(client.login,username='fuzzy', password='fuzzytest')
            login()
            self._run_tests(client, login=login)

            # superuser test
            print "####################################"
            print "## SUPERUSER #######################"
            print "####################################"
            login = functools.partial(client.login,username='fuzzyadmin', password='fuzzytest')
            login()
            self._run_tests(client, login=login)
        finally:
            self.user.delete()
            self.admin.delete()

    def _error(self, status, method, url, params, exception=None):
        print '\033[91m## {0:<3} {1:<4}  {2}  {3}'.format(status, method.upper(), url, unicode(params))
        traceback.print_exc()
        print '################################################################\033[0m'

    def _ok(self, status, method, url, params):
        if status <= 200:
            color = '\033[92m' # green
        else:      
            color = '\033[93m' # yellow
        print '{0}{1:<3}  {2:<4}  {3}  {4}\033[0m'.format(color, status, method.upper(), url, unicode(params))

    def _run_tests(self, client, login=None):
        for url, data in self.urls_info.iteritems():
            runned = False
            for method in ['get','post']:
                for t in self.TYPES.values():
                    params = {k:self.ir.random(t,5) for k in data.get(method)}
                    # prevent run of request without params few times
                    if not params and runned:
                        continue
                    elif not params:
                        runned = True
                    try:
                        res = getattr(client,method)(url,params, follow=True)
                    except Exception as e:
                        self._error(500, method, url, params, e)
                        if login:
                            login()
                    else:
                        if res.status_code >= 500:
                            self._error(res.status_code, method, url, params, e)
                        else:
                            status = res.status_code
                            _url = url
                            if res.redirect_chain:
                                redir, status = res.redirect_chain[0]
                                _url = "%s -> %s" % (url,redir) 
                            self._ok(status, method, _url, params)

                    if login and not client.session.get('_auth_user_id'):
                        login()
                        

