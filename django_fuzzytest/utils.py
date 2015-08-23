# -*- coding: utf-8 -*-
import itertools
from sre_constants import *
import sre_parse
import string
import random

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver, LocaleRegexURLResolver
from django.utils import translation
from django.core.exceptions import ViewDoesNotExist
from django.contrib.admindocs.views import simplify_regex

class RegexpInverter(object):

    category_chars = {
        CATEGORY_DIGIT : string.digits,
        CATEGORY_SPACE : string.whitespace,
        CATEGORY_WORD  : string.digits + string.letters + '_'
        }

    def _unique_extend(self, res_list, list):
        for item in list:
            if item not in res_list:
                res_list.append(item)

    def _handle_any(self, val):
        """
        This is different from normal regexp matching. It only matches
        printable ASCII characters.
        """
        return string.printable

    def _handle_branch(self, (tok, val)):
        all_opts = []
        for toks in val:
            opts = self._permute_toks(toks)
            self._unique_extend(all_opts, opts)
        return all_opts

    def _handle_category(self, val):
        return list(self.category_chars[val])

    def _handle_in(self, val):
        out = []
        for tok, val in val:
            out += self._handle_tok(tok, val)
        return out

    def _handle_literal(self, val):
        return [unichr(val)]

    def _handle_max_repeat(self, (min, max, val)):
        """
        Handle a repeat token such as {x,y} or ?.
        """
        subtok, subval = val[0]

        if max > 5000:
            # max is the number of cartesian join operations needed to be
            # carried out. More than 5000 consumes way to much memory.
            raise ValueError("To many repetitions requested (%d)" % max)

        optlist = self._handle_tok(subtok, subval)

        iterlist = []
        for x in range(min, max + 1):
            joined = self._join([optlist] * x)
            iterlist.append(joined)

        return (''.join(it) for it in itertools.chain(*iterlist))

    def _handle_range(self, val):
        lo, hi = val
        return (chr(x) for x in range(lo, hi + 1))

    def _handle_subpattern(self, val):
        return list(self._permute_toks(val[1]))

    def _handle_tok(self, tok, val):
        """
        Returns a list of strings of possible permutations for this regexp
        token.
        """
        handlers = {
            ANY        : self._handle_any,
            BRANCH     : self._handle_branch,
            CATEGORY   : self._handle_category,
            LITERAL    : self._handle_literal,
            IN         : self._handle_in,
            MAX_REPEAT : self._handle_max_repeat,
            RANGE      : self._handle_range,
            SUBPATTERN : self._handle_subpattern}
        try:
            return handlers[tok](val)
        except KeyError, e:
            fmt = "Unsupported regular expression construct: %s"
            raise ValueError(fmt % tok)

    def _permute_toks(self, toks):
        """
        Returns a generator of strings of possible permutations for this
        regexp token list.
        """
        lists = [self._handle_tok(tok, val) for tok, val in toks]
        return (''.join(it) for it in self._join(lists))

    def _join(self, iterlist):
        """
        Cartesian join as an iterator of the supplied sequences. Borrowed
        from:
        http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302478
        """
        def rloop(seqin, comb):
            if seqin:
                for item in seqin[0]:
                    newcomb = comb + [item]
                    for item in rloop(seqin[1:], newcomb):
                        yield item
            else:
                yield comb
        return rloop(iterlist, [])

    ########## PUBLIC API ####################

    def ipermute(self, p):
        toks = [tok_n_val for tok_n_val in sre_parse.parse(p)]
        return self._permute_toks(toks)

    def permute(self, p):
        return list(self.ipermute(p))

    def random(self, p, length):
        res = self.permute(p)
        return ''.join(random.choice(res) for i in xrange(length))

class UrlFinder(object):
    # TODO: Look at https://github.com/ierror/django-js-reverse

    def get_urls(self, exclude=None):

        if getattr(settings, 'ADMIN_FOR', None):
            settings_modules = [__import__(m, {}, {}, ['']) for m in settings.ADMIN_FOR]
        else:
            settings_modules = [settings]
          
        decorator = ['login_required']

        urlconf = "ROOT_URLCONF"

        views = []
        for settings_mod in settings_modules:
            try:
                urlconf = __import__(getattr(settings_mod, urlconf), {}, {}, [''])
            except Exception as e:
                if options.get('traceback', None):
                    import traceback
                    traceback.print_exc()
                print(style.ERROR("Error occurred while trying to load %s: %s" % (getattr(settings_mod, urlconf), str(e))))
                continue

            view_functions = self.extract_views_from_urlpatterns(urlconf.urlpatterns)
            for (func, regex, url_name) in view_functions:
                if hasattr(func, '__globals__'):
                    func_globals = func.__globals__
                elif hasattr(func, 'func_globals'):
                    func_globals = func.func_globals
                else:
                    func_globals = {}

                if hasattr(func, '__name__'):
                    func_name = func.__name__
                elif hasattr(func, '__class__'):
                    func_name = '%s()' % func.__class__.__name__
                else:
                    func_name = re.sub(r' at 0x[0-9a-f]+', '', repr(func))

                views.append({
                    "module":func.__module__, 
                    "method":func_name,
                    "name":url_name,
                    "regexp": regex,
                    "url":simplify_regex(regex)
                })

    def extract_views_from_urlpatterns(self, urlpatterns, base='', namespace=None):
        """
        Return a list of views from a list of urlpatterns.
        Each object in the returned list is a two-tuple: (view_func, regex)
        """
        views = []
        for p in urlpatterns:
            if isinstance(p, RegexURLPattern):
                try:
                    if not p.name:
                        name = p.name
                    elif namespace:
                        name = '{0}:{1}'.format(namespace, p.name)
                    else:
                        name = p.name
                    views.append((p.callback, base + p.regex.pattern, name))
                except ViewDoesNotExist:
                    continue
            elif isinstance(p, RegexURLResolver):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                if namespace and p.namespace:
                    _namespace = '{0}:{1}'.format(namespace, p.namespace)
                else:
                    _namespace = (p.namespace or namespace)
                if isinstance(p, LocaleRegexURLResolver):
                    for langauge in self.LANGUAGES:
                        with translation.override(langauge[0]):
                            views.extend(self.extract_views_from_urlpatterns(patterns, base + p.regex.pattern, namespace=_namespace))
                else:
                    views.extend(self.extract_views_from_urlpatterns(patterns, base + p.regex.pattern, namespace=_namespace))
            elif hasattr(p, '_get_callback'):
                try:
                    views.append((p._get_callback(), base + p.regex.pattern, p.name))
                except ViewDoesNotExist:
                    continue
            elif hasattr(p, 'url_patterns') or hasattr(p, '_get_url_patterns'):
                try:
                    patterns = p.url_patterns
                except ImportError:
                    continue
                views.extend(self.extract_views_from_urlpatterns(patterns, base + p.regex.pattern, namespace=namespace))
            else:
                raise TypeError("%s does not appear to be a urlpattern object" % p)
        return views

