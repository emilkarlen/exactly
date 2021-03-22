import subprocess
import unittest
from abc import ABC
from typing import List, Sequence

from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.string_source import sdvs as str_src_sdvs
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.command_executor import CommandExecutor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.parse.token import QuoteType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as str_src_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import \
    StringSourceOfStringAbsStx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatChecksStdin
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import PgmAndArgsAbsStx, \
    ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import FullProgramAbsStx, \
    ProgramOfPythonInterpreterAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfRichStringAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext
from exactly_lib_test.util.file_utils.test_resources.assertions import IsProcessExecutionFileWIthContents


class StdinTestSetupBase(ABC):
    def __init__(self,
                 exit_code: int,
                 command_executor_w_stdin_check: CommandExecutor,
                 ):
        self.exit_code = exit_code
        self.command_executor_w_stdin_check = command_executor_w_stdin_check

    @property
    def os_services_w_stdin_check(self) -> OsServices:
        return os_services_access.new_for_cmd_exe(self.command_executor_w_stdin_check)

    @property
    def proc_exe_env__w_stdin_check(self) -> ProcessExecutionArrangement:
        return ProcessExecutionArrangement(self.os_services_w_stdin_check)


class NoStdinTestSetup(StdinTestSetupBase):
    def __init__(self,
                 put: unittest.TestCase,
                 exit_code: int,
                 ):
        super().__init__(
            exit_code,
            CommandExecutorThatChecksStdin(
                put,
                asrt.equals(subprocess.DEVNULL),
            ))


class NonEmptyStdinTestSetupBase(StdinTestSetupBase, ABC):
    def __init__(self,
                 put: unittest.TestCase,
                 exit_code: int,
                 expected_full_stdin_contents: str,
                 ):
        super().__init__(
            exit_code,
            CommandExecutorThatChecksStdin(
                put,
                IsProcessExecutionFileWIthContents(expected_full_stdin_contents),
                exit_code=exit_code,
            )
        )

    @staticmethod
    def _program_w_stdin_syntax(pgm_and_args: PgmAndArgsAbsStx,
                                stdin_contents: str,
                                ) -> FullProgramAbsStx:
        return FullProgramAbsStx(
            pgm_and_args,
            stdin=str_src_abs_stx.StringSourceOfStringAbsStx.of_str_hard(stdin_contents),
        )


class SingleStdinOfProgramTestSetup(NonEmptyStdinTestSetupBase):
    STRING_SOURCE_CONTENTS = 'the contents of the string source'

    def __init__(self,
                 put: unittest.TestCase,
                 exit_code: int = 0,
                 additional_stdin: str = ''
                 ):
        super().__init__(put,
                         exit_code,
                         self.STRING_SOURCE_CONTENTS + additional_stdin)

    def program_w_stdin_syntax(self, pgm_and_args: PgmAndArgsAbsStx) -> FullProgramAbsStx:
        return self._program_w_stdin_syntax(
            pgm_and_args,
            self.STRING_SOURCE_CONTENTS,
        )


class MultipleStdinOfProgramTestSetup(NonEmptyStdinTestSetupBase):
    STR_SRC_CONTENTS__OF_REFERENCED_PROGRAM = 'the contents of the string source of the referenced program\n'
    STR_SRC_CONTENTS__OF_ARGUMENT = 'the contents of the string source of the argument\n'
    CONCATENATED_STRING_SOURCES_CONTENTS = ''.join([STR_SRC_CONTENTS__OF_REFERENCED_PROGRAM,
                                                    STR_SRC_CONTENTS__OF_ARGUMENT])

    def __init__(self,
                 put: unittest.TestCase,
                 exit_code: int = 0,
                 additional_stdin: str = ''
                 ):
        super().__init__(put, exit_code,
                         self.CONCATENATED_STRING_SOURCES_CONTENTS + additional_stdin)

        self.program_w_stdin_symbol = ProgramSymbolContext.of_sdv(
            'REFERENCED_PROGRAM',
            self._program_sdv_w_stdin__wo_sym_refs(
                self.STR_SRC_CONTENTS__OF_REFERENCED_PROGRAM
            ))

    @property
    def program_w_stdin_syntax(self) -> FullProgramAbsStx:
        return self._program_w_stdin_syntax(
            ProgramOfSymbolReferenceAbsStx(self.program_w_stdin_symbol.name),
            self.STR_SRC_CONTENTS__OF_ARGUMENT,
        )

    @property
    def program_symbol(self) -> ProgramSymbolContext:
        return self.program_w_stdin_symbol

    @staticmethod
    def _program_sdv_w_stdin__wo_sym_refs(contents_of_stdin: str) -> ProgramSdv:
        return program_sdvs.system_program(
            string_sdvs.str_constant('the-system-program'),
            stdin=[str_src_sdvs.ConstantStringStringSourceSdv(
                string_sdvs.str_constant(contents_of_stdin)
            )],
        )


class StdinCheckWithProgramWExitCode0ForSuccess:
    _SRC_FILE_REL_CONF = rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE)
    _CHECKER_PROGRAM_FILE_NAME = 'read-and-check-stdin.py'

    _CHECKER_PROGRAM_PY_SRC = """\
import sys

expected = sys.argv[1]

actual = sys.stdin.read()

if expected == actual:
  sys.exit(0)
else:
  sys.stderr.write('\\n'.join([
      'Expected: ' + repr(expected),
      'Actual  : ' + repr(actual),
  ]))
  sys.stderr.write('\\n')
  sys.exit(1)
"""

    def program_that_checks_stdin__syntax(self,
                                          program_stdin: str,
                                          additional_expected_stdin: str = '',
                                          ) -> FullProgramAbsStx:
        expected_contents_arg_syntax = ArgumentOfRichStringAbsStx.of_str(
            program_stdin + additional_expected_stdin, QuoteType.HARD
        )
        checker_pgm_syntax = ProgramOfPythonInterpreterAbsStx.of_execute_python_src_file(
            self._SRC_FILE_REL_CONF.path_abs_stx_of_name(self._CHECKER_PROGRAM_FILE_NAME),
            [expected_contents_arg_syntax],
        )
        return FullProgramAbsStx(
            checker_pgm_syntax,
            stdin=StringSourceOfStringAbsStx.of_str_hard(program_stdin)
        )

    @property
    def tcds_contents(self) -> TcdsPopulator:
        return self._SRC_FILE_REL_CONF.populator_for_relativity_option_root(
            DirContents([
                File(self._CHECKER_PROGRAM_FILE_NAME,
                     self._CHECKER_PROGRAM_PY_SRC)
            ])
        )

    @property
    def exit_code_of_successful_application(self) -> int:
        return 0


class StdinCheckViaCopyToOutputFileTestSetup:
    def __init__(self,
                 output_file: ProcOutputFile,
                 stdin_defined_for_program: Sequence[StringSourceSdv] = (),
                 ):
        self.output_file = output_file
        self._copy_program_symbol = ProgramSymbolContext.of_sdv(
            'COPY_STDIN',
            program_sdvs.for_py_source_on_command_line(py_programs.copy_stdin_to(output_file),
                                                       stdin=stdin_defined_for_program)
        )

    def program_that_copies_stdin_syntax(self) -> PgmAndArgsAbsStx:
        return ProgramOfSymbolReferenceAbsStx(self._copy_program_symbol.name)

    @property
    def symbols(self) -> List[SymbolContext]:
        return [self._copy_program_symbol]
