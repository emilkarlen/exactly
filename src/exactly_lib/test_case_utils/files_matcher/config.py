from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.test_case_utils.parse import rel_opts_configuration, path_relativities
from exactly_lib.util.cli_syntax.elements import argument as a

PATH_ARGUMENT = instruction_arguments.PATH_ARGUMENT

ACTUAL_RELATIVITY_CONFIGURATION = rel_opts_configuration.RelOptionArgumentConfiguration(
    path_relativities.PATH_ASSERTION_REL_OPTS_CONF,
    PATH_ARGUMENT.name,
    True)

EMPTINESS_CHECK_ARGUMENT = file_or_dir_contents.EMPTINESS_CHECK_ARGUMENT

NUM_FILES_CHECK_ARGUMENT = 'num-files'

NUM_FILES_ARGUMENT_CONSTANT = a.Constant(NUM_FILES_CHECK_ARGUMENT)

NUM_FILES_PROPERTY_NAME = 'number of files in dir'

EMPTINESS_PROPERTY_NAME = 'contents of dir'

MATCHES_ARGUMENT = 'matches'

MATCHES_FULL_OPTION = a.option('full')

SELECTION_OPTION = a.option('selection')

PRUNE_OPTION = a.option('with-pruned')

QUANTIFICATION_OVER_FILE_ARGUMENT = 'file'
