import vim, re

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

def is_word_char(char):
    return char.isalpha() or char.isdigit()

def shrink_spaces(string):
    return re.sub(r' +', r' ', string)

