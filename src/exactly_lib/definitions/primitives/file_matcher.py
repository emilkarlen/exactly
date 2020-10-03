from exactly_lib.util.cli_syntax.elements import argument as a
from . import matcher

WHOLE_PATH_MATCHER_NAME = 'path'
NAME_MATCHER_NAME = 'name'
STEM_MATCHER_NAME = 'stem'
SUFFIXES_MATCHER_NAME = 'suffixes'
SUFFIX_MATCHER_NAME = 'suffix'
TYPE_MATCHER_NAME = 'type'
PROGRAM_MATCHER_NAME = matcher.RUN_PROGRAM

PROGRAM_ARG_OPTION__LAST = a.Option(a.OptionName('path-arg-last'))
PROGRAM_ARG_OPTION__MARKER = a.Option(a.OptionName('path-arg-marker'), 'MARKER')
