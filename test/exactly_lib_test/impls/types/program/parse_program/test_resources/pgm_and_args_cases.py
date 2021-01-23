import sys
from typing import Callable, Sequence, List

from exactly_lib.impls.types.string_source import sdvs as str_src_sdvs
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.command import CommandDriver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import AssertionResolvingEnvironment, Arrangement, \
    arrangement_wo_tcds, arrangement_w_tcds, prim_asrt__constant
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.tcfs.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as pgm_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import PgmAndArgsAbsStx, \
    ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command


class PgmAndArgsCase:
    def __init__(self,
                 name: str,
                 pgm_and_args: PgmAndArgsAbsStx,
                 expected_command_driver: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
                 symbols: Sequence[SymbolContext] = (),
                 tcds: TcdsPopulator = tcds_populators.empty(),
                 mk_arrangement: Callable[[SymbolTable], Arrangement] =
                 lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
                 ):
        self.name = name
        self.pgm_and_args = pgm_and_args
        self.symbols = symbols
        self.expected_command_driver = expected_command_driver
        self.tcds = tcds
        self.mk_arrangement = mk_arrangement

    @staticmethod
    def wo_tcds(name: str,
                pgm_and_args: PgmAndArgsAbsStx,
                expected_command_driver: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
                symbols: Sequence[SymbolContext] = (),
                ) -> 'PgmAndArgsCase':
        return PgmAndArgsCase(
            name,
            pgm_and_args,
            expected_command_driver,
            symbols,
            tcds_populators.empty(),
            lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl)
        )

    @staticmethod
    def w_tcds(name: str,
               pgm_and_args: PgmAndArgsAbsStx,
               expected_command_driver: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
               tcds: TcdsPopulator,
               symbols: Sequence[SymbolContext] = (),
               ) -> 'PgmAndArgsCase':
        return PgmAndArgsCase(
            name,
            pgm_and_args,
            expected_command_driver,
            symbols,
            tcds,
            lambda sym_tbl: arrangement_w_tcds(symbols=sym_tbl,
                                               tcds_contents=tcds)
        )

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbols)

    @property
    def references_assertion(self) -> ValueAssertion[Sequence[SymbolReference]]:
        return SymbolContext.references_assertion_of_contexts(self.symbols)

    @property
    def usages_assertion(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return SymbolContext.usages_assertion_of_contexts(self.symbols)


def cases__w_argument_list__excluding_program_reference() -> List[PgmAndArgsCase]:
    """Cases of pgm-and-arg:s that have a list of arguments."""
    executable_file = fs.executable_file('executable-file', '')
    exe_file_relativity = rel_opt.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
    executable_file_ddv = path_ddvs.of_rel_option(exe_file_relativity.relativity,
                                                  path_ddvs.constant_path_part(executable_file.name)
                                                  )

    system_program = 'the-system-program'

    return [
        PgmAndArgsCase.w_tcds(
            'executable file',
            pgm_and_args=pgm_abs_stx.ProgramOfExecutableFileCommandLineAbsStx(
                exe_file_relativity.named_file_conf(executable_file.name).abstract_syntax
            ),
            expected_command_driver=lambda env: (
                asrt_command.matches_executable_file_command_driver(
                    asrt.equals(executable_file_ddv.value_of_any_dependency__d(env.tcds).primitive),
                )),
            tcds=exe_file_relativity.populator_for_relativity_option_root__hds(
                DirContents([executable_file])
            )
        ),
        PgmAndArgsCase.wo_tcds(
            '-python',
            pgm_and_args=pgm_abs_stx.ProgramOfPythonInterpreterAbsStx(()),
            expected_command_driver=prim_asrt__constant(
                asrt_command.matches_executable_file_command_driver(
                    asrt_path.path_as_str(asrt.equals(sys.executable)),
                )),
        ),
        PgmAndArgsCase.wo_tcds(
            'system program',
            pgm_and_args=pgm_abs_stx.ProgramOfSystemCommandLineAbsStx(
                StringLiteralAbsStx(system_program)
            ),
            expected_command_driver=prim_asrt__constant(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(system_program)
                ))
        ),
    ]


def program_reference__w_argument_list() -> PgmAndArgsCase:
    system_program = 'the-system-program'
    system_program_sdv = program_sdvs.system_program(string_sdvs.str_constant(system_program))
    system_program_symbol = ProgramSymbolContext.of_sdv('SYSTEM_PROGRAM_SYMBOL', system_program_sdv)

    return PgmAndArgsCase.wo_tcds(
        'reference to program w argument list',
        pgm_and_args=ProgramOfSymbolReferenceAbsStx(system_program_symbol.name),
        symbols=[system_program_symbol],
        expected_command_driver=prim_asrt__constant(
            asrt_command.matches_system_program_command_driver(
                asrt.equals(system_program)
            )),
    )


def program_sdv_w_stdin__wo_sym_refs(contents_of_stdin: str) -> ProgramSdv:
    return program_sdvs.system_program(
        string_sdvs.str_constant('the-system-program'),
        stdin=[str_src_sdvs.ConstantStringStringSourceSdv(
            string_sdvs.str_constant(contents_of_stdin)
        )],
    )


def cases__wo_argument_list() -> List[PgmAndArgsCase]:
    """Cases of pgm-and-arg:s that DO NOT have a list of arguments."""

    return [shell()]


def shell() -> PgmAndArgsCase:
    shell_command_line = 'the shell command line'

    return PgmAndArgsCase.wo_tcds(
        'shell',
        pgm_and_args=pgm_abs_stx.ProgramOfShellCommandLineAbsStx(
            StringLiteralAbsStx(shell_command_line)
        ),
        expected_command_driver=prim_asrt__constant(
            asrt_command.matches_shell_command_driver(asrt.equals(shell_command_line))
        )
    )


def cases__w_argument_list__including_program_reference() -> List[PgmAndArgsCase]:
    return cases__w_argument_list__excluding_program_reference() + [program_reference__w_argument_list()]


def cases_w_and_wo_argument_list__including_program_reference() -> List[PgmAndArgsCase]:
    return cases__w_argument_list__including_program_reference() + [shell()]


def cases_w_and_wo_argument_list__excluding_program_reference() -> List[PgmAndArgsCase]:
    return cases__w_argument_list__excluding_program_reference() + [shell()]
