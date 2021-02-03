from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.impls.instructions import source_file_relativities
from exactly_lib.impls.types.path.rel_opts_configuration import RelOptionArgumentConfiguration
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile

PROGRAM_OUTPUT_OPTIONS = {
    ProcOutputFile.STDOUT: a.OptionName('stdout-from'),
    ProcOutputFile.STDERR: a.OptionName('stderr-from'),
}
FILE_OPTION = a.OptionName('contents-of')
IGNORE_EXIT_CODE = program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME

SOURCE_FILE_ARGUMENT_NAME = a.Named('SOURCE-FILE-PATH')


def src_rel_opt_arg_conf_for_phase(phase_is_after_act: bool,
                                   default_relativity: RelOptionType = RelOptionType.REL_HDS_CASE,
                                   ) -> RelOptionArgumentConfiguration:
    return source_file_relativities.src_rel_opt_arg_conf_for_phase(
        default_relativity,
        SOURCE_FILE_ARGUMENT_NAME.name,
        phase_is_after_act,
    )
