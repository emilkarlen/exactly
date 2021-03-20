import unittest
from typing import Sequence, List

from exactly_lib.impls.types.files_source.defs import ModificationType
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.abstract_syntax import InstructionAbsStx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import IS_FAILURE, IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources import embryo_arr_exp
from exactly_lib_test.impls.types.files_source.test_resources import abstract_syntaxes as fs_abs_stx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opts
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import FileSystemElements
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import DefaultRelPathAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import \
    StringSourceSymbolContextOfPrimitiveConstant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestValidationOfContents(),
        TestSuccessfulApplication(),
        TestFailingApplication(),
    ])


class TestValidationOfContents(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        dst_path = DefaultRelPathAbsStx('existing-file')
        for phase_is_after_act in [False, True]:
            for modification_type in ModificationType:
                checker = integration_check.checker(phase_is_after_act)
                for validation_case in validation_cases.failing_validation_cases():
                    instruction_syntax = InstructionAbsStx(
                        dst_path,
                        fs_abs_stx.FileContentsExplicitAbsStx(modification_type,
                                                              validation_case.value.syntax),
                    )
                    # ACT & ASSERT #
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        embryo_arr_exp.Arrangement.phase_agnostic(
                            symbols=validation_case.value.symbol_context.symbol_table,
                        ),
                        embryo_arr_exp.MultiSourceExpectation.phase_agnostic(
                            validation=validation_case.value.assertion,
                            symbol_usages=validation_case.value.symbol_context.usages_assertion,
                        ),
                        sub_test_identifiers={
                            'modification_type': modification_type,
                            'phase_is_after_act': phase_is_after_act,
                            'validation': validation_case.name
                        },
                    )


class ContentsCase:
    def __init__(self,
                 name: str,
                 dst_file_name: str,
                 contents_syntax: fs_abs_stx.FileContentsAbsStx,
                 symbols: List[SymbolContext],
                 pre_existing_files: FileSystemElements,
                 expected_files: FileSystemElements = (),
                 ):
        self.name = name
        self.dst_file_name = dst_file_name
        self.contents_syntax = contents_syntax
        self.symbols = symbols
        self.pre_existing_files = pre_existing_files
        self.expected_files = expected_files


class TestSuccessfulApplication(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for case in successful_cases():
                dst_path = rel_conf.path_abs_stx_of_name(case.dst_file_name)
                instruction_syntax = InstructionAbsStx(
                    dst_path,
                    case.contents_syntax,
                )
                with self.subTest(case.name,
                                  phase_is_after_act=phase_is_after_act):
                    # ACT & ASSERT #
                    checker.check__abs_stx(
                        self,
                        instruction_syntax,
                        embryo_arr_exp.Arrangement.phase_agnostic(
                            symbols=SymbolContext.symbol_table_of_contexts(case.symbols),
                            tcds=TcdsArrangement(
                                non_hds_contents=rel_conf.populator_for_relativity_option_root__non_hds__s(
                                    case.pre_existing_files
                                )
                            ),
                        ),
                        embryo_arr_exp.Expectation.phase_agnostic(
                            symbol_usages=SymbolContext.usages_assertion_of_contexts(case.symbols),
                            main_result=IS_SUCCESS,
                            main_side_effects_on_sds=rel_conf.assert_root_dir_contains_exactly__p(
                                case.expected_files)
                        ),
                    )


class TestFailingApplication(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opts.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)
        for phase_is_after_act in [False, True]:
            checker = integration_check.checker(phase_is_after_act)
            for case in _failing_cases():
                dst_path = rel_conf.path_abs_stx_of_name(case.dst_file_name)
                instruction_syntax = InstructionAbsStx(
                    dst_path,
                    case.contents_syntax,
                )
                with self.subTest(case.name):
                    # ACT & ASSERT #
                    checker.check__abs_stx(
                        self,
                        instruction_syntax,
                        embryo_arr_exp.Arrangement.phase_agnostic(
                            symbols=SymbolContext.symbol_table_of_contexts(case.symbols),
                            tcds=TcdsArrangement(
                                non_hds_contents=rel_conf.populator_for_relativity_option_root__non_hds__s(
                                    case.pre_existing_files
                                )
                            ),
                        ),
                        embryo_arr_exp.Expectation.phase_agnostic(
                            symbol_usages=SymbolContext.usages_assertion_of_contexts(case.symbols),
                            main_result=IS_FAILURE,
                        )
                    )


def successful_cases() -> Sequence[ContentsCase]:
    return [
        _successful__create(),
        _successful__append(),
    ]


def _failing_cases() -> Sequence[ContentsCase]:
    contents_symbol = StringSourceSymbolContextOfPrimitiveConstant(
        'CONTENTS_SYMBOL',
        'added contents',
    )
    regular_file = fs.File.empty('regular-file')
    return [
        ContentsCase(
            'create',
            regular_file.name,
            fs_abs_stx.FileContentsExplicitAbsStx(
                ModificationType.CREATE,
                contents_symbol.abstract_syntax
            ),
            symbols=[contents_symbol],
            pre_existing_files=[regular_file],
        ),
        ContentsCase(
            'append',
            regular_file.name,
            fs_abs_stx.FileContentsExplicitAbsStx(
                ModificationType.APPEND,
                contents_symbol.abstract_syntax
            ),
            symbols=[contents_symbol],
            pre_existing_files=[],
        ),
    ]


def _successful__create() -> ContentsCase:
    contents_symbol = StringSourceSymbolContextOfPrimitiveConstant(
        'CONTENTS_SYMBOL',
        'contents',
    )
    created_file = fs.File('regular-file',
                           contents_symbol.contents_str)
    return ContentsCase(
        'create',
        created_file.name,
        fs_abs_stx.FileContentsExplicitAbsStx(
            ModificationType.CREATE,
            contents_symbol.abstract_syntax,
        ),
        symbols=[contents_symbol],
        pre_existing_files=[],
        expected_files=[created_file],
    )


def _successful__append() -> ContentsCase:
    contents_symbol = StringSourceSymbolContextOfPrimitiveConstant(
        'CONTENTS_SYMBOL',
        '<added contents>',
    )
    original_dst_file = fs.File('regular-file', 'original contents')
    modified_dst_file = fs.File(original_dst_file.name,
                                original_dst_file.contents + contents_symbol.contents_str)
    return ContentsCase(
        'append',
        original_dst_file.name,
        fs_abs_stx.FileContentsExplicitAbsStx(
            ModificationType.APPEND,
            contents_symbol.abstract_syntax,
        ),
        symbols=[contents_symbol],
        pre_existing_files=[original_dst_file],
        expected_files=[modified_dst_file],
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
