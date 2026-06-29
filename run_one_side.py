# -*- coding: utf-8 -*-

import sys
import traceback
import os
import linecache

module_path = r"Q:\PARAM_HYPER\py_functions"

if module_path not in sys.path:
    sys.path.append(module_path)

for mod_name in ["sc_common", "_one_side_"]:
    try:
        if mod_name in sys.modules:
            del sys.modules[mod_name]
    except:
        pass


DEBUG_EXTERNAL_MODULES = True

def trace_external_calls(frame, event, arg):
    if not DEBUG_EXTERNAL_MODULES:
        return None

    try:
        filename = frame.f_code.co_filename
        funcname = frame.f_code.co_name
        lineno = frame.f_lineno

        if filename is None:
            return trace_external_calls

        filename_l = filename.lower()

        if "py_functions" not in filename_l:
            return trace_external_calls

        if not (
            filename_l.endswith("_one_side_.py") or
            filename_l.endswith("sc_common.py")
        ):
            return trace_external_calls

        if event == "call":
            print("")
            print("[CALL] {}:{} -> {}".format(filename, lineno, funcname))

        elif event == "line":
            code_line = linecache.getline(filename, lineno).strip()
            print("[LINE] {}:{} | {}".format(os.path.basename(filename), lineno, code_line))

        elif event == "return":
            print("[RETURN] {}:{} -> {}".format(os.path.basename(filename), lineno, funcname))

        elif event == "exception":
            exc_type, exc_value, exc_tb = arg
            print("[EXCEPTION] {}:{} -> {}: {}".format(
                os.path.basename(filename),
                lineno,
                exc_type,
                exc_value
            ))

    except Exception as e:
        print("[TRACE_ERROR] {}".format(e))

    return trace_external_calls


try:
    import _one_side_

    _one_side_.inject_spaceclaim_globals(globals())

    print("Point em _one_side_:", "Point" in _one_side_.__dict__)
    print("com em _one_side_:", "com" in _one_side_.__dict__)
    print("Point em sc_common:", "Point" in _one_side_.com.__dict__)
    print("get_face_normal_safe em _one_side_:", "get_face_normal_safe" in _one_side_.__dict__)

    selection = Selection.GetActive()
    inlist = selection.GetItems[IDocObject]()
    onlist = len(inlist)

    if onlist >= 5:
        try:
            sys.settrace(trace_external_calls)
            _one_side_.main_function(selection)
        finally:
            sys.settrace(None)
    else:
        print("Erro: selecione 1 face alvo e 4 arestas válidas da extremidade.")

except Exception as e:
    sys.settrace(None)
    print("ERRO GERAL:")
    print(repr(e))
    traceback.print_exc()
    raise
