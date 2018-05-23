if !has('pythonx')
    echom "vim-smart-completer requires pythonx support"
    inoremap <silent> <Plug>(SC) <C-x><C-p>
    finish
endif

if exists("g:sc_loaded")
    finish
endif

let g:sc_loaded = 1

function! SetDefault(varname, default)
    if !exists(a:varname)
        exec "let ".a:varname."=".a:default
    endif
endfunction

function! SC_Init()
    call SetDefault("g:sc_auto_trigger", 1)
    call SetDefault("g:sc_auto_trigger_space_only", 1)
    call SetDefault("g:sc_pattern_length", 25)
    call SetDefault("g:sc_max_lines", 1000)
    call SetDefault("g:sc_max_results", 10)
    call SetDefault("g:sc_max_result_length", 50)
    call SetDefault("g:sc_max_downward_search", 10)
    call SetDefault("g:sc_preferred_result_length", 8)
    call SetDefault("g:sc_cursor_word_filter", 0)
    
pythonx << endpython
import vim
import re

def reverse(string):
    return string[::-1]

def clamp(x, a, b):
    if x < a: return a
    if x > b: return b
    return x

def safe_substr(string, a, b):
    return string[clamp(a, 0, len(string)) : clamp(b, 0, len(string))]

def safe_escape(string):
    string = string.replace('\\', '\\\\')
    string = string.replace('"', '\\"')
    
    return string

def strings_to_vimstr(strings):
    strings = [('"' + safe_escape(string) + '"') for string in strings]
    return '[' + (','.join(strings)) + ']'

def vim_setvar(varname, varstr):
    vim.command('let ' + varname + '=' + varstr)

def vim_getvar(varname):
    return vim.eval(varname)

def vim_setopt(optname, optstr):
    vim.command('set ' + optname + '=' + optstr)

def vim_getopt(optname):
    return vim.eval('&' + optname)

def vim_cursorline():
    return int(vim.eval('line(".")')) - 1
    
def vim_cursorcol():
    return int(vim.eval('col(".")')) - 1

def vim_complete(column, optionsstr, auto_select):
    completeopt_old = vim_getopt('completeopt')
    completeopt = 'menuone'
    if not auto_select:
        completeopt += ',noselect'
    
    vim_setopt('completeopt', completeopt)
    vim.command('silent call complete(' + str(column + 1) + ',' + optionsstr + ')')
    # if not auto_select:
        # vim.command('call feedkeys("\\<C-P>", "n")')
        
    vim_setopt('completeopt', completeopt_old)

def is_word_char(char):
    return char.isalpha() or char.isdigit()

def shrink_spaces(string):
    return re.sub(r' +', r' ', string)

class SmartContextCompleter:
    def __init__(self):
        self.ycm_auto_trigger_old = None
        self.completefunc_old = None
        self.next = []
    
    def disable_ycm(self):
        if self.ycm_auto_trigger_old != None:
            return
            
        vim.command('call SetDefault("g:ycm_auto_trigger", 1)')
        self.ycm_auto_trigger_old = vim_getvar('g:ycm_auto_trigger')
        
        vim_setvar('g:ycm_auto_trigger', '0')
        
    def restore_ycm(self):
        if self.ycm_auto_trigger_old == None:
            return
        
        vim_setvar('g:ycm_auto_trigger', self.ycm_auto_trigger_old)
        self.ycm_auto_trigger_old = None
        
    def setup_vars(self):
        self.auto_trigger            = int(vim_getvar('g:sc_auto_trigger'))
        self.auto_trigger_space_only = int(vim_getvar('g:sc_auto_trigger_space_only'))
        self.pattern_length          = int(vim_getvar('g:sc_pattern_length'))
        self.max_lines               = int(vim_getvar('g:sc_max_lines'))
        self.max_results             = int(vim_getvar('g:sc_max_results'))
        self.max_result_length       = int(vim_getvar('g:sc_max_result_length'))
        self.max_downward_search     = int(vim_getvar('g:sc_max_downward_search'))
        self.preferred_result_length = int(vim_getvar('g:sc_preferred_result_length'))
        self.cursor_word_filter      = int(vim_getvar('g:sc_cursor_word_filter'))
    
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
    
    def get_matches(self):
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
            while pat_cursor_word_len < patlen and is_word_char(patstr[pat_cursor_word_len]):
                pat_cursor_word_len += 1
        
        res = []
        resn = []
        
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
                            
                            # find insert position
                            ins = len(resn) - 1
                            while ins >= 0 and priority > resn[ins]:
                                ins -= 1
                            
                            ins += 1
                            if ins >= self.max_results: break
                            
                            # find option string
                            optstart = j + i + 1
                            opt = safe_substr(linestr, optstart, optstart + self.max_result_length)
                            
                            if len(opt) <= 0: break
                            
                            # simple repetition check
                            if ins < len(resn) and res[ins] == opt: break
                            
                            # insert option
                            resn.insert(ins, priority)
                            res.insert(ins, opt)
                        
                            if len(resn) > self.max_results:
                                resn.pop()
                                res.pop()
                            
                            break
                        
                        j = self.next[j]
                        matched = j
        
        for i in range(len(res)):
            res[i] = self.polish_result(res[i])
        
        return res
    
    def cf_findstart(self):
        vim_setvar('g:sc__retval', str(vim_cursorcol() + 1))

    def cf_getmatches(self):
        vim_setvar('g:sc__retval', strings_to_vimstr(self.get_matches()))
        vim_setopt('completefunc', self.completefunc_old)

    def complete(self, auto_select):
        # <-
        completeopt_old = vim_getopt('completeopt')
        completeopt = 'menuone'
        
        vim_setopt('completeopt', completeopt)
        
        # <-
        self.completefunc_old = vim_getopt('completefunc')
        completefunc = 'SC_CompleteFunc'
        
        vim_setopt('completefunc', completefunc)
        
        # <-
        vim.command('call feedkeys("\\<C-X>\\<C-U>", "n")')
        if not auto_select:
            vim.command('call feedkeys("\\<C-P>", "n")')
        # ->
            
        # ->
        
        vim_setopt('completeopt', completeopt_old)
        # ->
    
    def triggered(self):
        if not self.auto_trigger:
            return False
        
        if not self.auto_trigger_space_only:
            return True
        
        buf = vim.current.buffer
        
        line = vim_cursorline()
        col = vim_cursorcol()
        
        linestr = buf[line]
        if col >= 2:
            if linestr[col - 1] == ' ' and linestr[col - 2] != ' ':
                return True
        
        return False

sc = SmartContextCompleter()

endpython

endfunction

call SC_Init()

function! SC_Complete()
pythonx << endpython
sc.setup_vars()
sc.complete(True)
endpython

return ''
endfunction

function! SC_OnCursorMovedI()

pythonx << endpython
sc.setup_vars()

if sc.triggered():
    # sc.disable_ycm()
    sc.complete(False)

else:
    # sc.restore_ycm()
    pass
endpython

endfunction

function! SC_OnInsertLeave()

pythonx << endpython
sc.setup_vars()

# sc.restore_ycm()
endpython
    
endfunction

function! SC_CompleteFunc(findstart, base)
  
    let g:sc__findstart = a:findstart
    
pythonx << endpython
if int(vim_getvar('g:sc__findstart')) == 1:
    sc.cf_findstart()
else:
    sc.cf_getmatches()
endpython

    if a:findstart
        return g:sc__retval
    else
        return {'words': g:sc__retval, 'refresh': 'always'}
    endif
    
endfunction

" auto commands
autocmd CursorMovedI * call SC_OnCursorMovedI()
autocmd InsertLeave * call SC_OnInsertLeave()

" key binding
inoremap <silent> <Plug>(SC) <C-r>=SC_Complete()<cr>

