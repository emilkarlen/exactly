from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.impls.instructions.source_file_relativities import src_rel_opt_arg_conf_for_phase2
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile

CONTENTS_ASSIGNMENT_TOKEN = instruction_arguments.ASSIGNMENT_OPERATOR
PROGRAM_OUTPUT_OPTIONS = {
    ProcOutputFile.STDOUT: a.OptionName('stdout-from'),
    ProcOutputFile.STDERR: a.OptionName('stderr-from'),
}
FILE_OPTION = a.OptionName('file')
CONTENTS_ARGUMENT = 'CONTENTS'
IGNORE_EXIT_CODE = program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME

DEFAULT_SRC_REL_OPTION = RelOptionType.REL_CWD


def src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool,
                                   ) -> RelOptionArgumentConfiguration:
    return src_rel_opt_arg_conf_for_phase2(RelOptionType.REL_CWD,
                                           'SOURCE-FILE-PATH',
                                           phase_is_after_act)
