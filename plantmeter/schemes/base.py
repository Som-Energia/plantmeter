from __future__ import absolute_import


class BaseScheme(object):
    """Base scheme interface

    :param uri: URI to get the properties for the scheme 
    """
    def __init__(self, uri):
        pass

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError()

    def insert(self, document):
        raise NotImplementedError()

    def get(self, collection, filters, fields=None):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()