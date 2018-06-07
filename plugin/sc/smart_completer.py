import vim
import re

from util import *
from secondary_completers.secondary_completer import *
from secondary_completers.ycm import *
from completion_results import *

class SmartCompleter:
    def __init__(self, secondary):
        self.ycm_auto_trigger_old = None
        self.completefunc_old = None
        self.next = []
        
        self.secondary = secondary
        self.results = CompletionResults()
    
    def setup_vars(self):
        self.auto_trigger            = int(vim_getvar('g:sc_auto_trigger'))
        self.pattern_length          = int(vim_getvar('g:sc_pattern_length'))
        self.max_lines               = int(vim_getvar('g:sc_max_lines'))
        self.max_results             = int(vim_getvar('g:sc_max_results'))
        self.max_result_length       = int(vim_getvar('g:sc_max_result_length'))
        #  self.max_downward_search     = int(vim_getvar('g:sc_max_downward_search'))
        self.preferred_result_length = int(vim_getvar('g:sc_preferred_result_length'))
        self.cursor_word_filter      = int(vim_getvar('g:sc_cursor_word_filter'))
        
        self.results.set_max_entries(self.max_results)
    
    def polish_result(self, string):
        strlen = len(string)
        i = 0
        while i < strlen and string[i] == ' ': i += 1
        if i >= strlen:
            return ''
        
        preferred_length = self.preferred_result_length
        while i < strlen and (i < preferred_length or is_word_char(string[i])):
            if is_word_char(string[i]):
                preferred_length = 0
            
            i += 1
            
        return string[:i].rstrip()

    def generate_next_array(self, patstr):
        i = -1
        j = 0
        self.next[0] = -1
        patlen = len(patstr)
        while j < patlen:
            if i == -1 or patstr[i] == patstr[j]:
                i += 1
                j += 1
                self.next[j] = i
                
            else:
                i = self.next[i]
    
    def get_cursor_word_len(self):
        buf = vim.current.buffer
        line = buf[vim_cursorline()][:vim_cursorcol()]
        i = len(line) - 1
        result = 0
        while i >= 0 and is_word_char(line[i]):
            result += 1
            i -= 1
        
        return result
    
    def get_cursor_word(self):
        buf = vim.current.buffer
        return safe_substr(buf[vim_cursorline()], vim_cursorcol() - self.get_cursor_word_len(), vim_cursorcol())
    
    def cache_results(self):
        self.results.clear()
        
        if len(self.next) != self.pattern_length + 1:
            self.next = [0 for i in range(self.pattern_length + 1)]
            
        for i in range(self.pattern_length + 1):
            self.next[i] = 0
        
        buf = vim.current.buffer
        
        cursorline = vim_cursorline()
        cursorcol = vim_cursorcol()
        
        patstr = shrink_spaces(reverse(safe_substr(buf[cursorline], cursorcol - self.pattern_length, cursorcol)).rstrip())
        patlen = len(patstr)
        self.generate_next_array(patstr)
        patstr += '\0'
        
        pat_cursor_word_len = 0
        if self.cursor_word_filter == 1:
            pat_cursor_word_len = self.get_cursor_word_len()
        
        #  res = []
        #  resn = []
        
        linecnt = 0
        l = 1
        buflen = len(buf)
        while linecnt < self.max_lines:
            dlineidu = -(l // 2)
            dlineidd = -dlineidu
            
            lineidu = cursorline + dlineidu
            lineidd = cursorline + dlineidd
            
            l += 1
            
            if lineidu < 0 and lineidd >= buflen: break
            
            if (l & 1) == 1:
                lineid = lineidu
            
            else:
                lineid = lineidd
                # if dlineidd > self.max_downward_search and lineidu >= 0:
                    # continue
            
            if lineid < 0 or lineid >= buflen: continue
            
            linecnt += 1
            
            linestr = buf[lineid]
            if lineid == cursorline:
                linestr = linestr[:cursorcol - 1]
                
            linestr = shrink_spaces(linestr)
            linelen = len(linestr)
            
            i = linelen - 1
            j = 0
            matched = 0
            
            while i >= -1:
                if i >= 0 and linestr[i] == patstr[j]:
                    if linestr[i] != ' ': matched += 1
                    i -= 1
                    j += 1
                    
                else:
                    if j == 0:
                        i -= 1
                        
                    else:
                        # j = number of characters matched. also the position of first mismatched pattern char
                        # j + i + 1 = start of the potential completion string
                        
                        while True:
                            priority = matched
                            
                            # cursor word filters:
                            # discard results where word in text partially matches word at cursor
                            if j < pat_cursor_word_len:
                                break
                            
                            # discard results where word at cursor partially matches word in text
                            elif j == pat_cursor_word_len and i >= 0 and is_word_char(linestr[i]):
                                break
                            
                            optstart = j + i + 1
                            opt = safe_substr(linestr, optstart, optstart + self.max_result_length)
                            
                            self.results.add(opt, priority)
                            
                            """ legacy: cheesy insertion sort
                            # find insert position
                            ins = len(resn) - 1
                            while ins >= 0 and priority > resn[ins]:
                                ins -= 1
                            
                            ins += 1
                            if ins >= self.max_results: break
                            
                            # find option string
                            optstart = j + i + 1
                            opt = safe_substr(linestr, optstart, optstart + self.max_result_length)
                            if
                            
                            if len(opt) <= 0: break
                            
                            # simple repetition check
                            if ins < len(resn) and res[ins] == opt: break
                            
                            # insert option
                            resn.insert(ins, priority)
                            res.insert(ins, opt)
                        
                            if len(resn) > self.max_results:
                                resn.pop()
                                res.pop()
                            """
                            
                            break
                        
                        j = self.next[j]
                        matched = j
        
        return not self.results.is_empty()
    
    def cf_findstart(self):
        vim_setvar('g:sc__retval', str(vim_cursorcol() - self.get_cursor_word_len()))

    def cf_getmatches(self):
        res = self.results.get_strings()
        
        base = vim_getvar('g:sc__base')
        
        for i in range(len(res)):
            res[i] = base + self.polish_result(res[i])
        
        vim_setvar('g:sc__retval', strings_to_vimstr(res))
    
    def reset_complete_func(self):
        vim_setopt('completefunc', self.completefunc_old)

    def trigger(self, auto_select, use_secondary = False):
        if use_secondary or not self.cache_results():
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
        if not self.auto_trigger:
            return False
        
        # TODO no immediate trigger for now.
        return False
        
        buf = vim.current.buffer
        
        line = vim_cursorline()
        col = vim_cursorcol()
        
        linestr = buf[line]
        if col >= 2:
            if linestr[col - 1] == ' ' and linestr[col - 2] != ' ':
                return True
        
        return False
    
    def on_insertcharpre(self):
        self.secondary.disable()
    
    #  def disable_ycm(self):
        #  if self.ycm_auto_trigger_old != None:
            #  return
            
        #  vim.command('call SetDefault("g:ycm_auto_trigger", 1)')
        #  self.ycm_auto_trigger_old = vim_getvar('g:ycm_auto_trigger')
        
        #  vim_setvar('g:ycm_auto_trigger', '0')
        
    #  def restore_ycm(self):
        #  if self.ycm_auto_trigger_old == None:
            #  return
        
        #  vim_setvar('g:ycm_auto_trigger', self.ycm_auto_trigger_old)
        #  self.ycm_auto_trigger_old = None
    

smart_completer = SmartCompleter(YCMCompleter())

