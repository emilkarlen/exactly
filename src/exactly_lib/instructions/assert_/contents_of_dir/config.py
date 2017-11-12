from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_.utils import file_contents_resources
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a

PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_CWD,
            RelOptionType.REL_HOME_ACT,
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    PATH_ARGUMENT.name,
    True)

QUANTIFICATION_OVER_FILE_ARGUMENT = 'file'

NUM_FILES_CHECK_ARGUMENT = 'num-files'

NUM_FILES_ARGUMENT_CONSTANT = a.Constant(NUM_FILES_CHECK_ARGUMENT)

NUM_FILES_PROPERTY_NAME = 'number of files in dir'

EMPTINESS_PROPERTY_NAME = 'contents of dir'

NEGATION_OPERATOR = instruction_arguments.NEGATION_ARGUMENT_STR

SELECTION_OPTION = instruction_arguments.SELECTION_OPTION

EMPTINESS_CHECK_ARGUMENT = file_contents_resources.EMPTINESS_CHECK_ARGUMENT
