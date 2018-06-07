
from completion_results import *


class EditorInterface():
    
    """
    Interface for an editor (such as Vim).
    """
    
    def __init__(self):
        super(EditorInterface, self).__init__()
    
    def get_buffer(self):
        """
        Returns the buffer object, which can be accessed as a list of lines.
        """
        
        raise NotImplementedError
    
    def get_cursor_col(self):
        """
        Returns the cursor column index. 0-indexed.
        """
        
        raise NotImplementedError
    
    def get_cursor_line(self):
        """
        Returns the cursor line index. 0-indexed.
        """
        
        raise NotImplementedError
    
