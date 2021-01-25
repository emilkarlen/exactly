import unittest

from exactly_lib.impls.instructions.setup import stdin as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases import setup as setup_phase
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.setup.test_resources import instruction_check
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, SettingsBuilderAssertionModel, MultiSourceExpectation
from exactly_lib_test.impls.test_resources import abstract_syntaxes
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfFileAbsStx, \
    StringSourceOfStringAbsStx, CustomStringSourceAbsStx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_of_abs_stx
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case.result.test_resources import sh_assertions as asrt_sh
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringHereDocAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToFile),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToHereDoc),
        unittest.makeSuite(TestFailingInstructionExecution),
        TestStringSourceAsFileShouldRaiseHardErrorWhenFileDoNotExist(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def test_superfluous_arguments(self):
        valid_syntax = InstructionAbsStx(
            CustomStringSourceAbsStx.w_superfluous()
        )
        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, valid_syntax)

    def test_missing_value(self):
        valid_syntax = InstructionAbsStx(
            CustomStringSourceAbsStx.missing_value()
        )
        PARSE_CHECKER.check_invalid_syntax__abs_stx(self, valid_syntax)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestSuccessfulScenariosWithSetStdinToFile(TestCaseBaseForParser):
    def test_file__rel_non_hds(self):
        accepted_relativity_configurations = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT),
            rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP),
            rel_opt_conf.symbol_conf_rel_any(
                RelOptionType.REL_TMP,
                'SYMBOL',
                sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
        ]
        stdin_file = File('stdin.txt', 'contents of stdin / rel non-hds')

        for rel_conf in accepted_relativity_configurations:
            syntax = InstructionAbsStx(
                StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(stdin_file.name))
            )
            with self.subTest(option_string=rel_conf.option_argument):
                CHECKER.check_multi_source__abs_stx(
                    self,
                    syntax,
                    Arrangement(
                        tcds_contents=rel_conf.populator_for_relativity_option_root(DirContents([
                            stdin_file])),
                        symbols=rel_conf.symbols.in_arrangement(),
                    ),
                    MultiSourceExpectation(
                        symbols_after_parse=rel_conf.symbols.usages_expectation(),
                        settings_builder=AssertStdinIsPresentWithContents(
                            stdin_file.contents,
                            may_depend_on_external_resources=True),
                    ),
                )

    def test_file__rel_hds(self):
        accepted_relativity_configurations = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE),
            rel_opt_conf.default_conf_rel_any(RelOptionType.REL_HDS_CASE),
            rel_opt_conf.symbol_conf_rel_any(
                RelOptionType.REL_HDS_CASE,
                'SYMBOL',
                sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
        ]
        stdin_file = File('stdin.txt', 'contents of stdin / rel hds')
        for rel_conf in accepted_relativity_configurations:
            syntax = InstructionAbsStx(
                StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(stdin_file.name))
            )
            with self.subTest(option_string=rel_conf.option_argument):
                CHECKER.check_multi_source__abs_stx(
                    self,
                    syntax,
                    Arrangement(
                        hds_contents=hds_case_dir_contents(
                            DirContents([stdin_file])),
                        symbols=rel_conf.symbols.in_arrangement(),
                    ),
                    MultiSourceExpectation(
                        symbols_after_parse=rel_conf.symbols.usages_expectation(),
                        settings_builder=AssertStdinIsPresentWithContents(
                            stdin_file.contents,
                            may_depend_on_external_resources=True),
                    )
                )


class TestStringSourceAsFileShouldRaiseHardErrorWhenFileDoNotExist(TestCaseBaseForParser):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name('non-existing-file.txt'))
        )

        source_for_non_existing_file = remaining_source_of_abs_stx(syntax)
        parser = sut.Parser()
        proc_exe_arrangement = ProcessExecutionArrangement()
        # ACT & ASSERT #
        instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source_for_non_existing_file)
        self.assertIsInstance(instruction, SetupPhaseInstruction)
        with tcds_with_act_as_curr_dir() as path_resolving_environment:
            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                path_resolving_environment.tcds,
                SymbolTable.empty(),
                proc_exe_arrangement.process_execution_settings,
            )
            instruction_environment = environment_builder.build_post_sds()
            settings_builder = setup_phase.default_settings()

            main_result = instruction.main(instruction_environment,
                                           proc_exe_arrangement.os_services,
                                           settings_builder)

            asrt_sh.is_success().apply_with_message(self, main_result, 'main result')
            actual_stdin = settings_builder.stdin
            self.assertIsInstance(actual_stdin, StringSource, 'stdin should have been set')
            assert actual_stdin is not None

            with self.assertRaises(HardErrorException) as cm:
                path = actual_stdin.contents().as_file

            asrt_text_doc.is_any_text().apply_with_message(self, cm.exception.error,
                                                           'error message')


class TestSuccessfulScenariosWithSetStdinToHereDoc(TestCaseBaseForParser):
    def test_doc_without_symbol_references(self):
        content_line_of_here_doc = 'content line of here doc\n'
        syntax = InstructionAbsStx(
            StringSourceOfStringAbsStx(StringHereDocAbsStx(content_line_of_here_doc))
        )
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(),
            MultiSourceExpectation(
                settings_builder=AssertStdinIsPresentWithContents(
                    content_line_of_here_doc,
                    may_depend_on_external_resources=False,
                ),
            )
        )

    def test_doc_with_symbol_references(self):
        # ARRANGE #
        content_line_of_here_doc_template = 'content line of here doc with {symbol}\n'
        symbol = StringConstantSymbolContext('symbol_name', 'the symbol value')
        expected_stdin_contents = content_line_of_here_doc_template.format(symbol=symbol.str_value)
        expected_symbol_references = asrt.matches_singleton_sequence(
            symbol.reference_assertion__any_data_type
        )
        syntax = InstructionAbsStx(
            StringSourceOfStringAbsStx(StringHereDocAbsStx(
                content_line_of_here_doc_template.format(symbol=symbol.name__sym_ref_syntax)
            ))
        )
        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                symbols=symbol.symbol_table
            ),
            MultiSourceExpectation(
                settings_builder=AssertStdinIsPresentWithContents(
                    expected_stdin_contents,
                    may_depend_on_external_resources=False),
                symbols_after_parse=expected_symbol_references,
            )
        )


class TestFailingInstructionExecution(TestCaseBaseForParser):
    def test_referenced_file_does_not_exist__rel_hds(self):
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name('non-existing-file'))
        )

        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(),
            MultiSourceExpectation(
                validation=ValidationExpectationSvh.fails__pre_sds(),
            )
        )

    def test_referenced_file_does_not_exist__rel_symbol__post_sds(self):
        symbol_rel_opt = rel_opt_conf.symbol_conf_rel_any(
            RelOptionType.REL_ACT,
            'SYMBOL',
            sut.RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(symbol_rel_opt.path_abs_stx_of_name('non-existing-file'))
        )
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                symbols=symbol_rel_opt.symbols.in_arrangement(),
            ),
            MultiSourceExpectation(
                symbols_after_parse=symbol_rel_opt.symbols.usages_expectation(),
                validation=ValidationExpectationSvh.fails__post_sds(),
            ),
        )

    def test_referenced_file_is_a_directory(self):
        the_dir = Dir.empty('a-directory')
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(the_dir.name))
        )

        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                hds_contents=hds_case_dir_contents(DirContents([Dir.empty('directory')]))
            ),
            MultiSourceExpectation(
                validation=ValidationExpectationSvh.fails__pre_sds(),
            ),
        )


class AssertStdinIsPresentWithContents(ValueAssertionBase[SettingsBuilderAssertionModel]):
    def __init__(self,
                 expected: str,
                 may_depend_on_external_resources: bool
                 ):
        self._expectation = asrt_string_source.matches__str(
            asrt.equals(expected),
            asrt.equals(may_depend_on_external_resources),
        )

    def _apply(self,
               put: unittest.TestCase,
               value: SettingsBuilderAssertionModel,
               message_builder: asrt.MessageBuilder,
               ):
        stdin = value.actual.stdin
        put.assertIsNotNone(stdin,
                            message_builder.apply('stdin should be present'))
        self._expectation.apply(put, stdin, message_builder)


class InstructionAbsStx(AbstractSyntax):
    def __init__(self, value: StringSourceAbsStx):
        self._value = value

    def tokenization(self) -> TokenSequence:
        return abstract_syntaxes.AssignmentOfMandatoryValue(self._value).tokenization()


CHECKER = instruction_check.Checker(sut.Parser())
PARSE_CHECKER = parse_checker.Checker(sut.Parser())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
