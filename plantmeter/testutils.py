# -*- coding: utf-8 -*-

import unittest
from yamlns import namespace as ns

# Readable verbose testcase listing
unittest.TestCase.__str__ = unittest.TestCase.id


def assertNsEqual(self, dict1, dict2):
    """
    Asserts that both dict have equivalent structure.
    If parameters are strings they are parsed as yaml.
    Comparation by comparing the result of turning them
    to yaml sorting the keys of any dict within the structure.
    """
    def parseIfString(nsOrString):
        if isinstance(nsOrString, dict):
            return nsOrString
        return ns.loads(nsOrString)

    def sorteddict(d):
        if type(d) in (dict, ns):
            return ns(sorted(
                (k, sorteddict(v))
                for k, v in d.items()
            ))
        if type(d) in (list, tuple):
            return [sorteddict(x) for x in d]
        return d
    dict1 = sorteddict(parseIfString(dict1))
    dict2 = sorteddict(parseIfString(dict2))

    return self.assertMultiLineEqual(dict1.dump(), dict2.dump())


def _inProduction():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return 'somenergia' in socket.gethostbyaddr(s.getsockname()[0])[0].split('.')


def destructiveTest(decorated):
    return unittest.skipIf(_inProduction(),
                           "Destructive test being run in a production setup!!")(decorated)


# vim: ts=4 sw=4 et
