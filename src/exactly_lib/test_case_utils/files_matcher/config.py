from exactly_lib.definitions import instruction_arguments, logic
from exactly_lib.definitions.primitives.files_matcher import NUM_FILES_CHECK_ARGUMENT
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse import rel_opts_configuration
from exactly_lib.util.cli_syntax.elements import argument as a

PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    rel_opts_configuration.RelOptionsConfiguration(
        rel_opts_configuration.PathRelativityVariants({
            RelOptionType.REL_CWD,
            RelOptionType.REL_HDS_ACT,
            RelOptionType.REL_TMP,
            RelOptionType.REL_ACT,
        },
            True),
        RelOptionType.REL_CWD),
    PATH_ARGUMENT.name,
    True)

NUM_FILES_ARGUMENT_CONSTANT = a.Constant(NUM_FILES_CHECK_ARGUMENT)

NUM_FILES_PROPERTY_NAME = 'number of files in dir'

EMPTINESS_PROPERTY_NAME = 'contents of dir'

NEGATION_OPERATOR = logic.NOT_OPERATOR_NAME

SELECTION_OPTION = a.option('selection')

PRUNE_OPTION = a.option('prune')
