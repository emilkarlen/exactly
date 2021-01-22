from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramOfPythonInterpreterAbsStx, FullProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentOfStringAbsStx


class StdinCheckWithProgram:
    CHECKER_PROGRAM_FILE_NAME = 'read-and-check-stdin.py'

    CHECKER_PROGRAM_PY_SRC = """\
import sys

expected = sys.argv[1]

actual = sys.stdin.read()

if expected == actual:
  sys.exit(0)
else:
  sys.exit(1)
"""

    def __init__(self):
        self._src_file_rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE)

    def syntax_for_stdin_contents(self, stdin: str) -> ProgramAbsStx:
        expected_contents_arg_syntax = ArgumentOfStringAbsStx.of_str(stdin, QuoteType.HARD)
        checker_pgm_syntax = ProgramOfPythonInterpreterAbsStx.of_execute_python_src_file(
            self._src_file_rel_conf.path_abs_stx_of_name(self.CHECKER_PROGRAM_FILE_NAME),
            [expected_contents_arg_syntax],
        )
        return FullProgramAbsStx(
            checker_pgm_syntax,
            stdin=StringSourceOfStringAbsStx.of_str(stdin, QuoteType.HARD)
        )

    @property
    def tcds_contents(self) -> TcdsPopulator:
        return self._src_file_rel_conf.populator_for_relativity_option_root(
            DirContents([
                File(self.CHECKER_PROGRAM_FILE_NAME,
                     self.CHECKER_PROGRAM_PY_SRC)
            ])
        )

    @property
    def exit_code_of_successful_application(self) -> int:
        return 0
