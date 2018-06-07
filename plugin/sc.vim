let s:save_cpo = &cpo
set cpo&vim

function! s:restore_cpo()
  let &cpo = s:save_cpo
  unlet s:save_cpo
endfunction

function! s:fallback_mapping()
    inoremap <silent> <Plug>(SC) <C-x><C-p>
endfunction

if exists("g:sc_loaded")
    call s:restore_cpo()
    finish
elseif v:version <= 704
    echoe "Smart Completer requires higher version of Vim."
    call s:fallback_mapping()
    call s:restore_cpo()
    finish
elseif !has('timers')
    echoe "Smart Completer requires 'timer' feature of Vim."
    call s:fallback_mapping()
    call s:restore_cpo()
    finish
elseif !has('python') && !has('python3')
    echoe "Smart Completer requires 'python' or 'python3' support of Vim."
    call s:fallback_mapping()
    call s:restore_cpo()
    finish
elseif &encoding !~? 'utf-\?8'
    echoe "Smart Completer requires UTF-8 encoding. Include 'set encoding=utf-8' in your vimrc."
    call s:fallback_mapping()
    call s:restore_cpo()
    finish
endif

let g:sc_loaded = 1




let s:script_path = expand('<sfile>:p:h')
function! s:get_plugin_file(name)
    return s:script_path . '/' . a:name
endfunction

if has('python3')
    let s:pycmd = 'py3'
else
    let s:pycmd = 'py'
endif
let s:py = s:pycmd . ' '
let s:pyfile = s:pycmd . 'file '
let s:pyeof = s:pycmd . ' << endpython'

function! s:run_python_file(file)
    exe s:pyfile . s:get_plugin_file(a:file)
endfunction


function! s:set_default(varname, default)
    if !exists(a:varname)
        exec "let ".a:varname."=".a:default
    endif
endfunction

function! s:init()
    
    call s:set_default("g:sc_auto_trigger", 1)
    call s:set_default("g:sc_pattern_length", 25)
    call s:set_default("g:sc_max_lines", 1000)
    call s:set_default("g:sc_max_results", 12)
    call s:set_default("g:sc_max_result_length", 50)
    call s:set_default("g:sc_preferred_result_length", 8)
    call s:set_default("g:sc_cursor_word_filter", 1)
    
exe s:pyeof

from __future__ import absolute_import # make sure to import from top level
from __future__ import print_function # print as function
from __future__ import division # auto float division
from __future__ import unicode_literals

import os
import vim

script_path = vim.eval('s:script_path')
sys.path.insert(0, os.path.join(script_path, 'sc', 'secondary_completers')) # this allows local import
sys.path.insert(0, os.path.join(script_path, 'sc')) # this allows local import

endpython
    
    call s:run_python_file('sc/vim_smart_completer_controller.py')
    
    exe s:py . 'scc = VimSmartCompleterController()'
    exe s:py . 'scc.setup_vars()'
    
endfunction



" delayed trigger
let s:dt_t_id = -1

let s:dt_trigger_delay = 200
function! SC_dt_trigger(id)
    let s:dt_t_id = -1
    if !pumvisible() && (mode() ==# "i" || mode() ==# "R")
        call SC_Trigger_Auto()
    endif
    return ''
endfunction
function! s:dt_on_insertcharpre()
    exe s:py . 'scc.on_insertcharpre()'
    if s:dt_t_id != -1
        call timer_stop(s:dt_t_id)
    endif
    if g:sc_auto_trigger
        let s:dt_t_id = timer_start(s:dt_trigger_delay, 'SC_dt_trigger')
    endif
endfunction
" function! s:dt_on_insertcharpre()
    " " automatically close pop-up menu before inserting text
    " if pumvisible()
        " call feedkeys("\<C-E>", "in")
    " endif
" endfunction
augroup sc_dt_trigger_group
    autocmd!
    autocmd InsertCharPre * call s:dt_on_insertcharpre()
augroup END


function! SC_Trigger()
exe s:pyeof
# scc.setup_vars()
scc.trigger(True)
endpython

return ''
endfunction

function! SC_Trigger_Secondary()
exe s:pyeof
# scc.setup_vars()
scc.trigger(True, True)
endpython

return ''
endfunction

function! SC_Trigger_Auto()
exe s:pyeof
# scc.setup_vars()
scc.trigger(False)
endpython

return ''
endfunction

function! SC_OnCursorMovedI()

if !g:sc_auto_trigger
  return
endif

exe s:pyeof
# scc.setup_vars()

if scc.can_immediately_trigger():
    scc.trigger(False)

else:
    pass
endpython

endfunction

function! SC_OnInsertLeave()

exe s:pyeof
# scc.setup_vars()

endpython
    
endfunction

function! SC_CompleteFunc(findstart, base)
  
    let g:sc__findstart = a:findstart
    let g:sc__base = a:base
    
exe s:pyeof

if int(vim_getvar('g:sc__findstart')) == 1:
    scc.cf_findstart()

else:
    scc.cf_getmatches()
    scc.reset_complete_func()

endpython

    if a:findstart
        return g:sc__retval
    else
        return {'words': g:sc__retval}
    endif
    
endfunction


" init
call s:init()

" auto commands

augroup sc_group
  autocmd CursorMovedI * call SC_OnCursorMovedI()
  autocmd InsertLeave * call SC_OnInsertLeave()
augroup end

" key binding
inoremap <silent> <Plug>(SC) <C-r>=SC_Trigger()<cr>
inoremap <silent> <Plug>(SC_Secondary) <C-r>=SC_Trigger_Secondary()<cr>



call s:restore_cpo()
