import re
import json
from os.path import join, dirname


class Result(dict):
    def __init__(self, *args, **kwargs):
        super(Result, self).__init__(*args, **kwargs)
        for k, v in self.iteritems():
            setattr(self, k, v)


class Parser(object):
    def __init__(self, options):
        self.options = options
        self.pattern = options['regex']
        self.regex = re.compile(self.pattern)

    def parse(self, ua_string):
        result = self.regex.search(ua_string)
        matches = result is not None
        if not matches:
            return False, None
        opts = self.options
        family, major, minor, patch, patch_minor = (result.groups() + (None,) * 5)[:5]
        family_replacement = opts.get('family_replacement', opts.get('os_replacement', opts.get('device_replacement', None)))
        if family_replacement is not None:
            family = family_replacement.replace('$1', family or '$1')
        family = family if family else "Other"
        major = self.options.get('v1_replacement', major)
        minor = self.options.get('v2_replacement', minor)
        version = '.'.join(filter(bool, (major, minor, patch, patch_minor)))
        return matches, Result(
                            family=family,
                            major_version=major,
                            minor_version=minor,
                            patch_version=patch,
                            patch_minor_version=patch_minor,
                            version=version
                        )


REGEXES = json.load(open(join(dirname(__file__), 'resources', 'user_agent_data.json')))
PARSERS = {
    'browser': map(Parser, REGEXES['user_agent_parsers']),
    'device': map(Parser, REGEXES['device_parsers']),
    'os': map(Parser, REGEXES['os_parsers']),
}


def detect(ua_string):
    results = []
    for category, parser_list in PARSERS.items():
        empty_result = Result(family='Other' if category == 'browser' else None, major_version=None, minor_version=None, patch_version=None, patch_minor_version=None)
        for parser in parser_list:
            matches, result = parser.parse(ua_string)
            if matches:
                results.append((category, result))
                break
        else:
            results.append((category, empty_result))
    return Result(results)
