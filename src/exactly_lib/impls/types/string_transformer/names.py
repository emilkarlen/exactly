from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import program, string_transformer
from exactly_lib.util.cli_syntax.elements import argument as a

IDENTITY_TRANSFORMER_NAME = string_transformer.IDENTITY_TRANSFORMER_NAME
SEQUENCE_OPERATOR_NAME = string_transformer.SEQUENCE_OPERATOR_NAME
RUN_PROGRAM_TRANSFORMER_NAME = string_transformer.RUN_PROGRAM

RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME = program.WITH_IGNORED_EXIT_CODE_OPTION_NAME

REPLACE_TRANSFORMER_NAME = 'replace'
FILTER_TRANSFORMER_NAME = 'filter'
GREP_TRANSFORMER_NAME = 'grep'

RANGE_EXPR_SED_NAME = 'LINE-NUMBER-RANGE'
LINE_NUMBERS_FILTER_OPTION = a.Option(a.OptionName('line-nums'))

LINE_NUMBERS_FILTER__LIMIT_SEPARATOR = ':'

CHARACTER_CASE = 'char-case'
CHARACTER_CASE_TO_LOWER_OPTION_NAME = a.OptionName(long_name='to-lower')
CHARACTER_CASE_TO_UPPER_OPTION_NAME = a.OptionName(long_name='to-upper')

STRIP_SPACE = 'strip'
STRIP_TRAILING_SPACE_OPTION_NAME = a.OptionName(long_name='trailing-space')
STRIP_TRAILING_NEW_LINES_OPTION_NAME = a.OptionName(long_name='trailing-new-lines')

TCDS_PATH_REPLACEMENT = 'replace-test-case-dirs'

LINES_SELECTION_OPTION_NAME = a.OptionName(long_name='at')
LINES_SELECTION_OPTION = a.Option(LINES_SELECTION_OPTION_NAME,
                                  syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT.singular_name)

PRESERVE_NEW_LINES_OPTION_NAME = a.OptionName(long_name='preserve-new-lines')
PRESERVE_NEW_LINES_OPTION = a.Option(PRESERVE_NEW_LINES_OPTION_NAME)
