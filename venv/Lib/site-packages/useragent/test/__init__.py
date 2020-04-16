import json
from os.path import join, dirname

from useragent import detect


def load_resource(filename):
    return json.load(open(join(dirname(__file__), filename)))


def test_browser_results():
    for case in generate_test_cases(['test_browser.json', 'test_firefox.json', 'test_pgts_browser.json'], 'browser'):
        yield case


def test_os_results():
    for case in generate_test_cases(['test_os.json', 'test_additional_os.json'], 'os'):
        yield case


# def test_device_results():
#     for case in generate_test_cases(['test_device.json'], 'device'):
#         yield case


def generate_test_cases(resource_names, attr_name):
    test_cases = load_resource('test_os.json')['test_cases']
    test_cases += load_resource('test_additional_os.json')['test_cases']
    for resource in resource_names:
        for case in load_resource(resource)['test_cases']:
            yield validate_result, case['user_agent_string'], attr_name, case['family'], case['major'], case['minor'], case['patch'], case.get('patch_minor', None)


def validate_result(ua_string, attr_name, family, major, minor, patch, patch_minor):
    result = getattr(detect(ua_string), attr_name)
    assert result.family == family, "%s != %s" % (result.family, family)
    assert result.major_version == major
    assert result.minor_version == minor
    assert result.patch_version == patch
    assert result.patch_minor_version == patch_minor
