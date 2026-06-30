# -*- coding: utf-8 -*-

import sys
import traceback
import os
import linecache
from datetime import datetime

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

DEBUG_EXTERNAL_MODULES = True
EXPORT_FULL_LOG = True
now = datetime.now()

timestamp = "{0:04d}{1:02d}{2:02d}_{3:02d}{4:02d}{5:02d}_{6:06d}".format(
    now.year,
    now.month,
    now.day,
    now.hour,
    now.minute,
    now.second,
    now.microsecond
)

LOG_FILE = r"C:\temp\run_two_side_debug_{0}.log".format(timestamp)

# =============================================================================
# LOG
# =============================================================================

class Tee(object):

    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            try:
                f.write(obj)
                f.flush()
            except:
                pass

    def flush(self):
        for f in self.files:
            try:
                f.flush()
            except:
                pass


logfile = None

if EXPORT_FULL_LOG:

    try:

        if not os.path.exists(r"C:\temp"):
            os.makedirs(r"C:\temp")

        logfile = open(LOG_FILE, "w")

        sys.stdout = Tee(sys.stdout, logfile)
        sys.stderr = Tee(sys.stderr, logfile)

        print("")
        print("=" * 80)
        print("RUN_TWO_SIDE DEBUG LOG")
        print("=" * 80)
        print("Arquivo : {}".format(LOG_FILE))
        print("")

    except Exception as e:

        print("Falha ao iniciar log:")
        print(e)

# =============================================================================
# MÓDULOS
# =============================================================================

module_path = r"Q:\PARAM_HYPER\py_functions"

if module_path not in sys.path:
    sys.path.append(module_path)

for mod_name in ["sc_common", "_two_side_"]:

    try:

        if mod_name in sys.modules:
            del sys.modules[mod_name]

    except:
        pass

# =============================================================================
# TRACE
# =============================================================================

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
            filename_l.endswith("_two_side_.py") or
            filename_l.endswith("sc_common.py")
        ):
            return trace_external_calls

        if event == "call":

            print("")
            print("[CALL] {}:{} -> {}".format(
                filename,
                lineno,
                funcname
            ))

        elif event == "line":

            code_line = linecache.getline(
                filename,
                lineno
            ).strip()

            print("[LINE] {}:{} | {}".format(
                os.path.basename(filename),
                lineno,
                code_line
            ))

        elif event == "return":

            print("[RETURN] {}:{} -> {}".format(
                os.path.basename(filename),
                lineno,
                funcname
            ))
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

# =============================================================================
# EXECUÇÃO
# =============================================================================

try:

    import _two_side_

    _two_side_.inject_spaceclaim_globals(globals())

    print("Point em _two_side_:", "Point" in _two_side_.__dict__)
    print("com em _two_side_:", "com" in _two_side_.__dict__)
    print("Point em sc_common:", "Point" in _two_side_.com.__dict__)

    print(
        "get_face_normal_safe em _two_side_:",
        "get_face_normal_safe" in _two_side_.__dict__
    )

    selection = Selection.GetActive()
    inlist = selection.GetItems[IDocObject]()
    onlist = len(inlist)
    print("")
    print("Itens selecionados:", onlist)
    print("")

    # mínimo:
    # 2 faces alvo
    # arestas das duas extremidades
    if onlist >= 4:

        try:
            sys.settrace(trace_external_calls)
            _two_side_.main_function(selection)
        finally:
            sys.settrace(None)

    else:
        print("")
        print("Erro:")
        print("Selecione 2 faces alvo e as arestas abertas das 2 extremidades.")
        print("Itens selecionados: {}".format(onlist))
        print("")

except Exception as e:

    sys.settrace(None)
    print("")
    print("ERRO GERAL:")
    print(repr(e))
    traceback.print_exc()
    raise

finally:

    if logfile is not None:

        try:
            print("")
            print("=" * 80)
            print("FIM DO LOG")
            print("=" * 80)
            logfile.close()

        except:
            pass
