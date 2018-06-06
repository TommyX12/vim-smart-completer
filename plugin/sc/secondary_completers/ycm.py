import vim

from secondary_completer import *

class YCMCompleter(SecondaryCompleter):
    """
    The YouCompleteMe completer.
    """
    
    def __init__(self):
        super(YCMCompleter, self).__init__()
    
    def trigger(self):
        """
        Triggers the completer to start completion.
        """
        # manually dispatch TextChangedI event for YCM to use.
        vim.command('do TextChangedI')
        
    def enable(self):
        """
        Enables the completer.
        """
        vim.command('let g:ycm_auto_trigger = 1')
        
    def disable(self):
        """
        Disables the completer.
        """
        vim.command('let g:ycm_auto_trigger = 0')
