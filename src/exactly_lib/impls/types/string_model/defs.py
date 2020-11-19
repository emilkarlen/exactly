from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile

PROGRAM_OUTPUT_OPTIONS = {
    ProcOutputFile.STDOUT: a.OptionName('stdout-from'),
    ProcOutputFile.STDERR: a.OptionName('stderr-from'),
}
FILE_OPTION = a.OptionName('file')
IGNORE_EXIT_CODE = program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME
