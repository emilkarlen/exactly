from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_utils.parse.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile

CONTENTS_ASSIGNMENT_TOKEN = instruction_arguments.ASSIGNMENT_OPERATOR
PROGRAM_OUTPUT_OPTIONS = {
    ProcOutputFile.STDOUT: a.OptionName('stdout-from'),
    ProcOutputFile.STDERR: a.OptionName('stderr-from'),
}
FILE_OPTION = a.OptionName('file')
CONTENTS_ARGUMENT = 'CONTENTS'
SRC_PATH_ARGUMENT = a.Named('SOURCE-FILE-PATH')
IGNORE_EXIT_CODE = program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME
_SRC_REL_OPTIONS__BEFORE_ACT = set(RelOptionType).difference({RelOptionType.REL_RESULT})
_SRC_REL_OPTIONS__AFTER_ACT = set(RelOptionType)


def src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool) -> RelOptionArgumentConfiguration:
    rel_option_types = _SRC_REL_OPTIONS__AFTER_ACT if phase_is_after_act else _SRC_REL_OPTIONS__BEFORE_ACT
    return src_rel_opt_arg_conf(rel_option_types)


def src_rel_opt_arg_conf(rel_option_types: set) -> RelOptionArgumentConfiguration:
    return RelOptionArgumentConfiguration(
        RelOptionsConfiguration(PathRelativityVariants(
            rel_option_types,
            True),
            RelOptionType.REL_CWD),
        SRC_PATH_ARGUMENT.name,
        True)
