"""
These Bridges class methods are working on multiple processors
that can be located remotely
"""


class Bridges:

    @staticmethod
    def create(manager=None, workers=None, name=None):
        raise NotImplementedError

    @staticmethod
    def set(manager=None, workers=None, name=None):
        raise NotImplementedError

    @staticmethod
    def list(hosts=None):
        raise NotImplementedError

    @staticmethod
    def check(hosts=None):
        raise NotImplementedError

    @staticmethod
    def restart(host=None):
        raise NotImplementedError
