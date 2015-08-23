# coding: utf-8
from __future__ import unicode_literals
import time
import logging
import traceback
from optparse import make_option
import json

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from django_fuzzytest.runner import FuzzyRunner

logger = logging.getLogger(__file__)


class Command(BaseCommand):
    help = 'Run fuzzytest'

    option_list = BaseCommand.option_list + (
        make_option("--exclude", "-e", action="append", default=[], 
            dest="exclude", help="Exclude applications from test"),
        make_option("--cache", "-c", action="store_true", default='.fuzzycache', 
            dest="cache", help="Cache path. Default: .fuzzycache"),
    )

    params = {} 

    def _merge_cache(self, path):
        fp = file(path)
        for line in fp:
            d = json.loads(line)
            self.params.setdefault(
                d['path'],
                {"get":[],"post":[],"files":[]}
            )
            self.params[d['path']]['get'] = list(set( \
                self.params[d['path']]['get'] + d['get']))
            self.params[d['path']]['post'] = list(set( \
                self.params[d['path']]['post'] + d['post']))
            self.params[d['path']]['post'] = list(set( \
                self.params[d['path']]['post'] + d['post']))

    def handle(self, *args, **options):
        exclude = options.get('exclude')
        cache_path = options.get('cache')
        self._merge_cache(cache_path)

        runner = FuzzyRunner(self.params)
        runner.run()
