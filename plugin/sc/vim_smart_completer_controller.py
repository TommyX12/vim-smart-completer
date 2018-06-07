import vim
import re

from util import *
from secondary_completers.secondary_completer import *
from secondary_completers.ycm import *
from completion_results import *
from editor_interface import *
from smart_completer import *

def vim_setvar(varname, varstr):
    vim.command('let ' + varname + '=' + varstr)

def vim_getvar(varname):
    return vim.eval(varname)

def vim_setopt(optname, optstr):
    vim.command('set ' + optname + '=' + optstr)

def vim_getopt(optname):
    return vim.eval('&' + optname)


class VimSmartCompleterController(EditorInterface):
    
    """
    The completer controller for smart completer in Vim.
    Works closely with the vim plugin file.
    Contains interface for the Vim editor.
    """
    
    def __init__(self):
        self.completefunc_old = None
        
        self.primary = SmartCompleter(self)
        self.secondary = YCMCompleter()
    
    def setup_vars(self):
        self.auto_trigger                    = int(vim_getvar('g:sc_auto_trigger'))
        self.primary.pattern_length          = int(vim_getvar('g:sc_pattern_length'))
        self.primary.max_lines               = int(vim_getvar('g:sc_max_lines'))
        self.primary.max_result_length       = int(vim_getvar('g:sc_max_result_length'))
        self.primary.preferred_result_length = int(vim_getvar('g:sc_preferred_result_length'))
        self.primary.cursor_word_filter      = int(vim_getvar('g:sc_cursor_word_filter'))
        
        self.primary.results.set_max_entries(int(vim_getvar('g:sc_max_results')))
    
    def cf_findstart(self):
        vim_setvar('g:sc__retval', str(self.get_cursor_col() - self.primary.get_cursor_word_len()))

    def cf_getmatches(self):
        res = self.primary.results.get_strings()
        
        base = vim_getvar('g:sc__base')
        
        for i in range(len(res)):
            res[i] = base + self.primary.polish_result(res[i])
        
        vim_setvar('g:sc__retval', strings_to_vimstr(res))
    
    def reset_complete_func(self):
        vim_setopt('completefunc', self.completefunc_old)

    def trigger(self, auto_select, use_secondary = False):
        if use_secondary or not self.primary.cache_results():
            self.secondary.enable()
            self.secondary.trigger()
            return
            
        completeopt_old = vim_getopt('completeopt')
        completeopt = 'menuone'
        
        self.completefunc_old = vim_getopt('completefunc')
        completefunc = 'SC_CompleteFunc'
        
        vim_setopt('completeopt', completeopt)
        vim_setopt('completefunc', completefunc)
        
        if auto_select:
            vim.command('call feedkeys("\\<C-X>\\<C-U>", "in")')
        
        else:
            vim.command('call feedkeys("\\<C-X>\\<C-U>\\<C-P>", "in")')
        
        vim_setopt('completeopt', completeopt_old)
    
    def can_immediately_trigger(self):
        # TODO no immediate trigger for now.
        #  return self.primary.can_immediately_trigger()
        return False
    
    def on_insertcharpre(self):
        self.secondary.disable()
    
    def get_buffer(self):
        """
        @override
        """
        
        return vim.current.buffer
    
    def get_cursor_col(self):
        """
        @override
        """
        
        return int(vim.eval('col(".")')) - 1
    
    def get_cursor_line(self):
        """
        @override
        """
        
        return int(vim.eval('line(".")')) - 1
    

scc = VimSmartCompleterController()
