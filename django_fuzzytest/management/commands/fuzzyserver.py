# coding: utf-8
from __future__ import unicode_literals
import time
import logging
import sys
import traceback
from optparse import make_option
from functools import partial
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError

logger = logging.getLogger(__file__)

class RequestCacheMiddleware(object):

    PATH = None
    
    def process_request(self, request):
        """Saves all request data on request destruction"""
        res = {
            'post':request.POST.copy().keys(),
            'get':request.GET.copy().keys(),
            'files':request.FILES.copy().keys(),
            'path':request.path
        }
    
        file(self.PATH,'a').write("%s\n" % json.dumps(res))


class Command(BaseCommand):
    help = 'Run fuzzy server to cache all params passed with requests'

    option_list = BaseCommand.option_list + (
        make_option("--cache", "-c", action="store_true", default='.fuzzycache', 
            dest="cache", help="Cache path. Default: .fuzzycache"),
        make_option("--server", "-s", action="store_true", default='runserver', 
            dest="server", help="Command to run the debug server. Default: runserver")
    )
        
    def run_from_argv(self, argv):
        self.execute(*argv)

    def patch_request(self, path):
        RequestCacheMiddleware.PATH = path
        settings.MIDDLEWARE_CLASSES += ('django_fuzzytest.management.commands.fuzzyserver.RequestCacheMiddleware',) 
        print 'Added intercept middleware.'

    def handle(self, *args, **options):
        prog, command = sys.argv[0], sys.argv[1]
        parser = self.create_parser('asds', command)
        # ignore invalid options
        parser.error = lambda x:None
        args = sys.argv[2:]
        options,_ = parser.parse_args(args)
        cache_path = options.cache
        self.patch_request(cache_path)
        # pass execution to the runserver
        try:
            call_command('runserver',*args)
        except CommandError as e:
            print "Comand runserver got error: %s" % e

