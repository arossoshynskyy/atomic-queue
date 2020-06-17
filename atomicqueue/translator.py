class Translator:
    """ Class used to translate to ring buffer event types.
    This must be implemented by the publisher and passed as 
    an argument to the publish method """

    def translate(self, event, **kwargs):
        raise NotImplementedError()
