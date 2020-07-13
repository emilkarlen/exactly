from exactly_lib.util.cli_syntax.elements import argument as a
from . import matcher

NAME_MATCHER_NAME = 'name'
TYPE_MATCHER_NAME = 'type'
PROGRAM_MATCHER_NAME = matcher.RUN_PROGRAM

PROGRAM_ARG_OPTION__LAST = a.Option(a.OptionName('path-arg-last'))
PROGRAM_ARG_OPTION__MARKER = a.Option(a.OptionName('path-arg-marker'), 'MARKER')
