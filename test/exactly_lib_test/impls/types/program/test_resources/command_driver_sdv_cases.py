from typing import Callable, Sequence

from exactly_lib.impls.types.program.command import driver_sdvs
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.program.sdv.command import CommandDriverSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.command import CommandDriver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import AssertionResolvingEnvironment, Arrangement, \
    arrangement_w_tcds, arrangement_wo_tcds
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command


class CommandDriverSdvCase:
    def __init__(self,
                 name: str,
                 command_driver: CommandDriverSdv,
                 expected_command_driver: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
                 mk_arrangement: Callable[[SymbolTable], Arrangement],
                 ):
        self.name = name
        self.command_driver = command_driver
        self.expected_command_driver = expected_command_driver
        self.mk_arrangement = mk_arrangement


def all_command_driver_types() -> Sequence[CommandDriverSdvCase]:
    # ARRANGE #
    system_program_name = 'system-program'
    executable_program_file_name = 'executable-program-file'
    executable_file_relativity = relativity_options.conf_rel_any(RelOptionType.REL_HDS_ACT)
    executable_file_ddv = path_ddvs.of_rel_option(
        executable_file_relativity.relativity_option,
        path_ddvs.constant_path_part(executable_program_file_name)
    )
    shell_initial_command = 'shell initial command'

    def mk_arrangement__executable_file(symbols: SymbolTable) -> Arrangement:
        return arrangement_w_tcds(
            symbols=symbols,
            tcds_contents=executable_file_relativity.populator_for_relativity_option_root(
                fs.DirContents([fs.executable_file(executable_program_file_name)])
            )
        )

    def expected_command_driver__system_program(env: AssertionResolvingEnvironment
                                                ) -> ValueAssertion[CommandDriver]:
        return asrt_command.matches_system_program_command_driver(
            asrt.equals(system_program_name)
        )

    def expected_command_driver__executable_file(env: AssertionResolvingEnvironment
                                                 ) -> ValueAssertion[CommandDriver]:
        return asrt_command.matches_executable_file_command_driver(
            asrt.equals(executable_file_ddv.value_of_any_dependency__d(env.tcds).primitive),
        )

    def expected_command_driver__shell_cmd_line(env: AssertionResolvingEnvironment
                                                ) -> ValueAssertion[CommandDriver]:
        return asrt_command.matches_shell_command_driver(
            asrt.equals(shell_initial_command)
        )

    return [
        CommandDriverSdvCase(
            'system program',
            command_driver=driver_sdvs.CommandDriverSdvForSystemProgram(
                string_sdvs.str_constant(system_program_name)
            ),
            expected_command_driver=expected_command_driver__system_program,
            mk_arrangement=lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
        ),
        CommandDriverSdvCase(
            'executable program file',
            command_driver=driver_sdvs.CommandDriverSdvForExecutableFile(
                path_sdvs.constant(executable_file_ddv)
            ),
            expected_command_driver=expected_command_driver__executable_file,
            mk_arrangement=mk_arrangement__executable_file,
        ),
        CommandDriverSdvCase(
            'shell command line',
            command_driver=driver_sdvs.CommandDriverSdvForShell(
                string_sdvs.str_constant(shell_initial_command)
            ),
            expected_command_driver=expected_command_driver__shell_cmd_line,
            mk_arrangement=lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
        ),
    ]
