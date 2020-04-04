#
# These methods are not parallel but just work in one processor
#

class Bridge:

    @staticmethod
    def create(master=None, worker=None, name=None):
        """
        if host is missing the master is set up only
        if master is missing only the worker is set up

        :param master:
        :param host:
        :param name:
        :return:
        """
        raise NotImplementedError

    @staticmethod
    def set(master=None, worker=None, name=None):
        raise NotImplementedError

    @staticmethod
    def list(host=None):
        raise NotImplementedError

    @staticmethod
    def check(host=None):
        raise NotImplementedError

    @staticmethod
    def restart(host=None):
        raise NotImplementedError
