import unittest

from exactly_lib.impls.instructions.setup import stdin as sut
from exactly_lib.impls.types.path import path_relativities
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.setup.test_resources import instruction_check
from exactly_lib_test.impls.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation, MultiSourceExpectation
from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.impls.test_resources import abstract_syntaxes
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfFileAbsStx, \
    CustomStringSourceAbsStx, StringSourceOfHereDocAbsStx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_settings
from exactly_lib_test.test_case.test_resources.settings_builder_assertions import SettingsBuilderAssertionModel
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringHereDocAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import \
    StringSourceSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestInvalidSyntax),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToFile),
        unittest.makeSuite(TestSuccessfulScenariosWithSetStdinToHereDoc),
        TestSuccessfulScenariosWithSetStdinToStringSourceReference(),
        unittest.makeSuite(TestFailingInstructionExecution),
        TestActExeInputWStdinAsFileShouldBeInvalidWhenFileDoNotExist(),
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


class TestSuccessfulScenariosWithSetStdinToStringSourceReference(TestCaseBaseForParser):
    def runTest(self):
        string_source_symbol = StringSourceSymbolContextOfPrimitiveConstant(
            'STRING_SOURCE_SYMBOL',
            'the contents of the source'
        )
        syntax = InstructionAbsStx(
            string_source_symbol.abstract_syntax
        )
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                symbols=string_source_symbol.symbol_table,
            ),
            MultiSourceExpectation(
                symbols_after_parse=string_source_symbol.usages_assertion,
                settings_builder=_stdin_is_present_and_valid(
                    string_source_symbol.contents_str,
                    may_depend_on_external_resources=False),
            ),
        )


class TestSuccessfulScenariosWithSetStdinToFile(TestCaseBaseForParser):
    def test_file__rel_non_hds(self):
        accepted_relativity_configurations = [
            rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT),
            rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP),
            rel_opt_conf.symbol_conf_rel_any(
                RelOptionType.REL_TMP,
                'SYMBOL',
                RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
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
                        settings_builder=_stdin_is_present_and_valid(
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
                RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants),
        ]
        stdin_file = File('stdin.txt', 'contents of stdin / rel hds')
        for rel_conf in accepted_relativity_configurations:
            syntax = InstructionAbsStx(
                StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(stdin_file.name))
            )
            with self.subTest(option_string=rel_conf.option_argument.as_str):
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
                        settings_builder=_stdin_is_present_and_valid(
                            stdin_file.contents,
                            may_depend_on_external_resources=True),
                    )
                )


class TestActExeInputWStdinAsFileShouldBeInvalidWhenFileDoNotExist(TestCaseBaseForParser):
    def runTest(self):
        # ARRANGE #
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_ACT)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name('non-existing-stdin-file.txt'))
        )
        # ACT & ASSERT #
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                symbols=rel_conf.symbols.in_arrangement(),
            ),
            MultiSourceExpectation(
                symbols_after_parse=rel_conf.symbols.usages_expectation(),
                settings_builder=asrt_settings.stdin_is_present_but_invalid(),
            )
        )


class TestSuccessfulScenariosWithSetStdinToHereDoc(TestCaseBaseForParser):
    def test_doc_without_symbol_references(self):
        content_line_of_here_doc = 'content line of here doc\n'
        syntax = InstructionAbsStx(
            StringSourceOfHereDocAbsStx(StringHereDocAbsStx(content_line_of_here_doc))
        )
        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(),
            MultiSourceExpectation(
                settings_builder=_stdin_is_present_and_valid(
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
            symbol.reference_assertion__w_str_rendering
        )
        syntax = InstructionAbsStx(
            StringSourceOfHereDocAbsStx(StringHereDocAbsStx(
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
                settings_builder=_stdin_is_present_and_valid(
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
            RELATIVITY_OPTIONS_CONFIGURATION.options.accepted_relativity_variants)
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
                settings_builder=asrt_settings.stdin_is_present_but_invalid(),
            ),
        )

    def test_referenced_file_is_a_directory__pre_sds(self):
        the_dir = Dir.empty('a-directory')
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_HDS_CASE)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(the_dir.name))
        )

        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                tcds_contents=rel_conf.populator_for_relativity_option_root(
                    DirContents([the_dir])
                ),
            ),
            MultiSourceExpectation(
                validation=ValidationExpectationSvh.fails__pre_sds(),
            ),
        )

    def test_referenced_file_is_a_directory__post_sds(self):
        the_dir = Dir.empty('a-directory')
        rel_conf = rel_opt_conf.conf_rel_any(RelOptionType.REL_TMP)
        syntax = InstructionAbsStx(
            StringSourceOfFileAbsStx(rel_conf.path_abs_stx_of_name(the_dir.name))
        )

        CHECKER.check_multi_source__abs_stx(
            self,
            syntax,
            Arrangement(
                tcds_contents=rel_conf.populator_for_relativity_option_root(
                    DirContents([the_dir])
                ),
            ),
            MultiSourceExpectation(
                settings_builder=asrt_settings.stdin_is_present_but_invalid(),
            ),
        )


class InstructionAbsStx(InstructionArgsAbsStx):
    def __init__(self, value: StringSourceAbsStx):
        self._value = value

    def tokenization(self) -> TokenSequence:
        return abstract_syntaxes.AssignmentOfMandatoryValue(self._value).tokenization()


RELATIVITY_OPTIONS_CONFIGURATION = path_relativities.ALL_REL_OPTIONS_ARG_CONFIG

CHECKER = instruction_check.Checker(sut.Parser())
PARSE_CHECKER = parse_checker.Checker(sut.Parser())


def _stdin_is_present_and_valid(expected: str,
                                may_depend_on_external_resources: bool,
                                ) -> Assertion[SettingsBuilderAssertionModel]:
    return asrt_settings.stdin_is_present_and_valid(
        asrt_string_source.matches__str(
            contents=asrt.equals(expected),
            may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
        )
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
