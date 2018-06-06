import vim

class SecondaryCompleter(object):
    """
    Interface for a secondary completer.
    """
    
    def __init__(self):
        super(SecondaryCompleter, self).__init__()
        
    def trigger(self):
        """
        Triggers the completer to start completion.
        """
        raise NotImplementedError
        
    def enable(self):
        """
        Enables the completer.
        """
        raise NotImplementedError
        
    def disable(self):
        """
        Disables the completer.
        """
        raise NotImplementedError
