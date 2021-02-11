def traceback_as_str() -> str:
    import sys
    import io
    import traceback
    exc_info = sys.exc_info()
    string_io = io.StringIO()
    traceback.print_exception(*exc_info, file=string_io)
    return string_io.getvalue()
