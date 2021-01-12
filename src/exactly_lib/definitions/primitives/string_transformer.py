from exactly_lib.definitions.entity import types
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from . import program

IDENTITY_TRANSFORMER_NAME = 'identity'
SEQUENCE_OPERATOR_NAME = '|'
RUN_PROGRAM = program.RUN_PROGRAM_PRIMITIVE

STRING_TRANSFORMER_ARGUMENT = a.Named(types.STRING_TRANSFORMER_TYPE_INFO.syntax_element_name)

STRING_TRANSFORMATION_ARGUMENT = a.Named('TRANSFORMATION')

WITH_TRANSFORMED_CONTENTS_OPTION_NAME = a.OptionName(long_name='transformed-by')

WITH_TRANSFORMED_CONTENTS_OPTION = option_syntax.option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME)

TRANSFORMATION_OPTION = a.Option(WITH_TRANSFORMED_CONTENTS_OPTION_NAME,
                                 argument=types.STRING_TRANSFORMER_TYPE_INFO.syntax_element_name)

WITH_IGNORED_EXIT_CODE_OPTION_NAME = program.WITH_IGNORED_EXIT_CODE_OPTION_NAME
