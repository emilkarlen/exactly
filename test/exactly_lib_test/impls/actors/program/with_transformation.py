import unittest

from exactly_lib.impls.actors.program import actor as sut
from exactly_lib.tcfs.path_relativity import RelOptionType, RelHdsOptionType
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.execution.test_resources import eh_assertions as asrt_eh
from exactly_lib_test.impls.actors.test_resources import integration_check
from exactly_lib_test.impls.actors.test_resources.integration_check import Expectation, PostSdsExpectation, \
    arrangement_w_tcds
from exactly_lib_test.impls.types.program.test_resources import arguments_building as args
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_transformer.test_resources.test_transformers_setup import \
    TO_UPPER_CASE_TRANSFORMER
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.test_case.result.test_resources import failure_details_assertions as asrt_failure_details
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_proc_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers
from exactly_lib_test.util.test_resources import py_program


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTransformerShouldBeAppliedToStdout(),
        TestHardErrorInTransformerShouldResultInHardErrorOfExecute(),
    ])


class TestTransformerShouldBeAppliedToStdout(unittest.TestCase):
    def runTest(self):
        for exit_code in [0, 1, 72]:
            with self.subTest(exit_code=exit_code):
                self._check_with_exit_code(exit_code)

    def _check_with_exit_code(self, exit_code: int):
        # ARRANGE #
        result = SubProcessResult(
            exitcode=exit_code,
            stdout='output on stdout',
            stderr='output on stderr',
        )

        command_py_program = py_program.program_that_prints_and_exits_with_exit_code(result)

        py_file = fs.File(
            'the-program.py',
            command_py_program,
        )
        program_wo_transformation = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL',
            program_sdvs.interpret_py_source_file_that_must_exist(
                path_sdvs.of_rel_option_with_const_file_name(
                    RelOptionType.REL_HDS_CASE,
                    py_file.name,
                )
            )
        )

        source = args.program(
            args.symbol_ref_command_line(program_wo_transformation.name),
            transformation=TO_UPPER_CASE_TRANSFORMER.name__sym_ref_syntax)

        symbols = [
            program_wo_transformation,
            TO_UPPER_CASE_TRANSFORMER,
        ]
        # ACT & ASSERT #

        integration_check.check_execution(
            self,
            sut.actor(),
            [instr(source.as_arguments.lines)],
            arrangement_w_tcds(
                symbol_table=SymbolContext.symbol_table_of_contexts(symbols),
                hds_contents=hds_populators.contents_in(
                    RelHdsOptionType.REL_HDS_CASE,
                    DirContents([py_file]),
                )
            ),
            Expectation(
                symbol_usages=SymbolContext.references_assertion_of_contexts(symbols),
                execute=asrt_eh.is_exit_code(result.exitcode),
                post_sds=PostSdsExpectation.constant(
                    sub_process_result_from_execute=asrt_proc_result.matches_proc_result(
                        exit_code=asrt.equals(result.exitcode),
                        stdout=asrt.equals(result.stdout.upper()),
                        stderr=asrt.equals(result.stderr),
                    )
                )
            ),
        )


class TestHardErrorInTransformerShouldResultInHardErrorOfExecute(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        command_py_program = py_program.exit_with_code(0)

        py_file = fs.File(
            'the-program.py',
            lines_content(command_py_program),
        )
        program_wo_transformation = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL',
            program_sdvs.interpret_py_source_file_that_must_exist(
                path_sdvs.of_rel_option_with_const_file_name(
                    RelOptionType.REL_HDS_CASE,
                    py_file.name,
                )
            )
        )

        error_message = 'error message from transformer'
        transformer = StringTransformerPrimitiveSymbolContext(
            'HARD_ERROR_TRANSFORMER',
            string_transformers.model_access_raises_hard_error(error_message),
        )

        source = args.program(
            args.symbol_ref_command_line(program_wo_transformation.name),
            transformation=transformer.name__sym_ref_syntax)

        symbols = [
            program_wo_transformation,
            transformer,
        ]

        # ACT & ASSERT #

        integration_check.check_execution(
            self,
            sut.actor(),
            [instr(source.as_arguments.lines)],
            arrangement_w_tcds(
                symbol_table=SymbolContext.symbol_table_of_contexts(symbols),
                hds_contents=hds_populators.contents_in(
                    RelHdsOptionType.REL_HDS_CASE,
                    DirContents([py_file]),
                )
            ),
            Expectation(
                symbol_usages=SymbolContext.references_assertion_of_contexts(symbols),
                execute=asrt_eh.matches_hard_error(
                    asrt_failure_details.is_failure_message_matching__td(
                        asrt_text_doc.is_string_for_test_that_equals(error_message)
                    )
                ),
            ),
        )
