import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.abstract_syntax import \
    InstructionArgumentsAbsStx
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.actual_file_relativities import \
    RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.instruction_check import CHECKER
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import MultiSourceExpectation, \
    ExecutionExpectation
from exactly_lib_test.impls.types.string_matcher.test_resources.abstract_syntaxes import EmptyAbsStx
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangementPostAct
from exactly_lib_test.tcfs.test_resources.sub_dir_of_sds_act import \
    MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY
from exactly_lib_test.test_case.result.test_resources import pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct2
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import \
    StringMatcherSymbolContextOfPrimitiveConstant


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        InvalidActualFileAndSymbolReferences(),
        ValidActualFileAndSymbolReferences(),
    ])


class InvalidActualFileAndSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actual_file_name = 'actual'
        invalid_file_cases = [
            NameAndValue(
                'file does not exist',
                [],
            ),
            NameAndValue(
                'file is a dir',
                [Dir.empty(actual_file_name)],
            ),
            NameAndValue(
                'sym-link to dir',
                [
                    Dir.empty('a-dir'),
                    fs.sym_link(actual_file_name, 'a-dir')
                ],
            ),
            NameAndValue(
                'broken sym-link',
                [fs.sym_link(actual_file_name, 'non-existing-target')],
            ),
        ]
        for invalid_file_case in invalid_file_cases:
            for rel_conf in RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE:
                with self.subTest(invalid_cause=invalid_file_case,
                                  path_variant=rel_conf.name):
                    CHECKER.check__abs_stx__source_variants(
                        self,
                        InstructionArgumentsAbsStx(
                            rel_conf.path_abs_stx_of_name(actual_file_name),
                            EmptyAbsStx(),
                        ),
                        ArrangementPostAct2(
                            symbols=rel_conf.symbols.in_arrangement(),
                            tcds=TcdsArrangementPostAct(
                                tcds_contents=rel_conf.populator_for_relativity_option_root(
                                    DirContents(invalid_file_case.value)),
                                post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                            )
                        ),
                        MultiSourceExpectation(
                            symbol_usages=rel_conf.symbols.usages_expectation(),
                            execution=ExecutionExpectation.validation_corresponding_to_dsp__post_sds_as_hard_error(
                                rel_conf.directory_structure_partition,
                            )
                        ),
                    )


class ValidActualFileAndSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actual_file_name = 'actual'
        file_type_cases = [
            NameAndValue(
                'regular file',
                [fs.File.empty(actual_file_name)],
            ),
            NameAndValue(
                'sym-link to regular file',
                [
                    fs.File.empty('a-regular-file'),
                    fs.sym_link(actual_file_name, 'a-regular-file')
                ],
            ),
        ]
        for file_type_case in file_type_cases:
            for rel_conf in RELATIVITY_OPTION_CONFIGURATIONS_FOR_ACTUAL_FILE:
                for matcher_result in [False, True]:
                    matcher_symbol = StringMatcherSymbolContextOfPrimitiveConstant('STRING_MATCHER', matcher_result)
                    all_symbols = list(rel_conf.symbols.contexts_for_arrangement()) + [matcher_symbol]
                    with self.subTest(file_type=file_type_case,
                                      path_variant=rel_conf.name,
                                      matcher_result=matcher_result):
                        CHECKER.check__abs_stx__source_variants(
                            self,
                            InstructionArgumentsAbsStx(
                                rel_conf.path_abs_stx_of_name(actual_file_name),
                                matcher_symbol.abstract_syntax,
                            ),
                            ArrangementPostAct2(
                                symbols=SymbolContext.symbol_table_of_contexts(all_symbols),
                                tcds=TcdsArrangementPostAct(
                                    tcds_contents=rel_conf.populator_for_relativity_option_root(
                                        DirContents(file_type_case.value)),
                                    post_population_action=MK_SUB_DIR_OF_ACT_AND_MAKE_IT_CURRENT_DIRECTORY,
                                )
                            ),
                            MultiSourceExpectation(
                                symbol_usages=SymbolContext.usages_assertion_of_contexts(all_symbols),
                                execution=ExecutionExpectation(
                                    main_result=asrt_pfh.is_pass_of_fail(matcher_symbol.result_value)
                                )
                            ),
                        )
