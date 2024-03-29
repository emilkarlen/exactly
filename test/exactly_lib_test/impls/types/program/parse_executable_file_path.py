import sys
import unittest
from typing import Sequence, List

from exactly_lib.definitions import path as path_texts
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.impls.types.program.command import command_sdvs
from exactly_lib.impls.types.program.parse import parse_executable_file_path as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.references import path_relativity_restriction
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.program.test_resources import parse_executable_file_path_cases as utils
from exactly_lib_test.impls.types.program.test_resources.parse_executable_file_path_cases import \
    RelativityConfiguration, \
    suite_for, \
    ExpectationOnExeFile
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators as tcds_pop
from exactly_lib_test.test_resources.argument_renderer import CustomOptionArgument
from exactly_lib_test.test_resources.files.paths import non_existing_absolute_path
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.layout import LayoutSpec, STANDARD_LAYOUT_SPECS
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as asrt_str
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources import ddv_assertions
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restrictions
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import PathStringAbsStx, \
    RelOptPathAbsStx, \
    RelSymbolPathAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import PgmAndArgsAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramOfExecutableFileCommandLineAbsStx, ProgramOfPythonInterpreterAbsStx, PgmAndArgsWArgumentsAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfRichStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    test_case_configurations = [
        CONFIGURATION_FOR_PYTHON_EXECUTABLE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE,
        CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE,
    ]
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParseValidSyntaxWithoutArguments))
    ret_val.addTest(unittest.makeSuite(TestParseWithSymbols))
    ret_val.addTest(unittest.makeSuite(TestParseInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestParseAbsolutePath))
    for tc_conf in test_case_configurations:
        ret_val.addTests(suite_for_test_case_configuration(tc_conf))
    ret_val.addTests(suite_for(conf)
                     for conf in configurations())
    return ret_val


class TestCaseConfiguration:
    def __init__(self,
                 executable: PgmAndArgsAbsStx,
                 validation_result: validation.Expectation,
                 path_ddv: PathDdv,
                 expected_symbol_references: List[SymbolReference],
                 ):
        self.executable = executable
        self.path_ddv = path_ddv
        self.expected_symbol_references = expected_symbol_references
        self.validation_result = validation_result


def suite_for_test_case_configuration(configuration: TestCaseConfiguration) -> unittest.TestSuite:
    cases = [
        NoParenthesesAndNoFollowingArguments,
        NoParenthesesAndFollowingArguments,
    ]
    return unittest.TestSuite([
        tc(configuration)
        for tc in cases
    ])


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 expectation: ExpectationOnExeFile,
                 source_after_parse: Assertion[ParseSource]):
        self.name = name
        self.source = source
        self.expectation = expectation
        self.source_after_parse = source_after_parse

    @staticmethod
    def of(name: str,
           executable_file: PathAbsStx,
           arguments: Sequence[ArgumentAbsStx],
           expectation: ExpectationOnExeFile,
           source_after_parse: Assertion[ParseSource],
           ) -> 'Case':
        return Case(
            name,
            ProgramOfExecutableFileCommandLineAbsStx(
                executable_file,
                arguments
            ).tokenization().layout(LayoutSpec.of_default()),
            expectation,
            source_after_parse,
        )


class TestParseValidSyntaxWithoutArguments(unittest.TestCase):
    def test(self):
        cases = [
            Case.of(
                'absolute_path',
                PathStringAbsStx(StringLiteralAbsStx.of_shlex_quoted(sys.executable)),
                arguments=(),
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_ddvs.absolute_file_name(sys.executable),
                    expected_symbol_references=[],
                ),
                source_after_parse=asrt_source.is_at_end_of_line(1),
            ),
            Case.of(
                'without_option',
                PathStringAbsStx.of_plain_str('file'),
                arguments=[ArgumentOfRichStringAbsStx.of_str('arg2')],
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_of_default_relativity('file'),
                    expected_symbol_references=[],
                ),
                source_after_parse=has_remaining_part_of_first_line('arg2'),
            ),
            Case.of(
                'relative_file_name_with_space',
                PathStringAbsStx(StringLiteralAbsStx('the file', QuoteType.SOFT)),
                arguments=(),
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_of_default_relativity('the file'),
                    expected_symbol_references=[],
                ),
                source_after_parse=asrt_source.is_at_end_of_line(1),
            ),
            Case.of(
                'relative_file_name_with_space_and_arguments',
                PathStringAbsStx(StringLiteralAbsStx('the file', QuoteType.SOFT)),
                arguments=[ArgumentOfRichStringAbsStx.of_str('an argument', QuoteType.SOFT)],
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_of_default_relativity('the file'),
                    expected_symbol_references=[],
                ),
                source_after_parse=has_remaining_part_of_first_line('"an argument"'),
            ),
            Case.of(
                'option_without_tail',
                RelOptPathAbsStx(RelOptionType.REL_HDS_CASE, 'THE_FILE'),
                arguments=(),
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_of(RelOptionType.REL_HDS_CASE, 'THE_FILE'),
                    expected_symbol_references=[],
                ),
                source_after_parse=asrt_source.is_at_end_of_line(1),
            ),
            Case.of(
                'option_with_tail',
                RelOptPathAbsStx(RelOptionType.REL_CWD, 'FILE'),
                arguments=[ArgumentOfRichStringAbsStx.of_str('tail')],
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_of(RelOptionType.REL_CWD, 'FILE'),
                    expected_symbol_references=[],
                ),
                source_after_parse=has_remaining_part_of_first_line('tail'),
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseWithSymbols(unittest.TestCase):
    def test(self):
        file_symbol = ConstantSuffixPathDdvSymbolContext('file_symbol',
                                                         RelOptionType.REL_TMP,
                                                         'first_path_component')
        string_symbol = StringConstantSymbolContext('string_symbol',
                                                    'string symbol value')
        reference_of_relativity_symbol = SymbolReference(
            file_symbol.name,
            path_relativity_restriction(
                syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.accepted_relativity_variants
            ))
        reference_of_path_string_symbol_as_path_component = SymbolReference(
            string_symbol.name,
            ReferenceRestrictionsOnDirectAndIndirect(
                direct=value_restrictions.is_string(),
                indirect=value_restrictions.is_string()),
        )
        symbols = SymbolContext.symbol_table_of_contexts([
            file_symbol,
            string_symbol,
        ])
        cases = [
            Case.of(
                'symbol references in file',
                RelSymbolPathAbsStx(file_symbol.name, string_symbol.name__sym_ref_syntax),
                arguments=(),
                expectation=
                ExpectationOnExeFile(
                    path_ddv=path_ddvs.stacked(file_symbol.ddv,
                                               path_ddvs.constant_path_part(string_symbol.str_value)),
                    expected_symbol_references=[reference_of_relativity_symbol,
                                                reference_of_path_string_symbol_as_path_component],
                    symbol_for_value_checks=symbols,
                ),
                source_after_parse=asrt_source.is_at_end_of_line(1),
            ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                _parse_and_check(self, case)


class TestParseInvalidSyntax(unittest.TestCase):
    def test_missing_file_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().parse(ParseSource(path_texts.REL_HDS_CASE_OPTION))

    def test_invalid_option(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.parser().parse(ParseSource('{} FILE'.format(CustomOptionArgument('invalid-option'))))


CONFIGURATION_FOR_PYTHON_EXECUTABLE = TestCaseConfiguration(
    ProgramOfPythonInterpreterAbsStx(()),
    validation_result=validation.Expectation.passes_all(),
    path_ddv=path_ddvs.absolute_file_name(sys.executable),
    expected_symbol_references=[],
)

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_EXISTING_EXECUTABLE_FILE = TestCaseConfiguration(
    ProgramOfExecutableFileCommandLineAbsStx(
        PathStringAbsStx.of_plain_str(
            sys.executable, QuoteType.HARD,
        )
    ),
    validation_result=validation.Expectation.passes_all(),
    path_ddv=path_ddvs.absolute_file_name(sys.executable),
    expected_symbol_references=[],
)

_ABSOLUT_PATH_THAT_DOES_NOT_EXIST = str(non_existing_absolute_path('/absolute/path/that/is/expected/to/not/exist'))

CONFIGURATION_FOR_ABSOLUTE_PATH_OF_NON_EXISTING_FILE = TestCaseConfiguration(
    ProgramOfExecutableFileCommandLineAbsStx(
        PathStringAbsStx.of_plain_str(
            _ABSOLUT_PATH_THAT_DOES_NOT_EXIST, QuoteType.HARD,
        )
    ),
    validation_result=validation.Expectation.pre_eds(False),
    path_ddv=path_ddvs.absolute_file_name(_ABSOLUT_PATH_THAT_DOES_NOT_EXIST),
    expected_symbol_references=[],
)


class ExecutableTestBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: TestCaseConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _arg(self, template: str) -> str:
        return template.format(executable=self.configuration.executable)


class NoParenthesesAndNoFollowingArguments(ExecutableTestBase):
    def runTest(self):
        utils.check__abs_stx(
            self,
            self.configuration.executable,
            utils.Arrangement(tcds_pop.empty()),
            utils.Expectation(
                path_ddv=self.configuration.path_ddv,
                expected_symbol_references=self.configuration.expected_symbol_references,
                source=asrt_source.is_at_end_of_line(1),
                validation_result=self.configuration.validation_result,
            ),
        )


class NoParenthesesAndFollowingArguments(ExecutableTestBase):
    def runTest(self):
        instruction_argument = PgmAndArgsWArgumentsAbsStx(
            self.configuration.executable,
            [ArgumentOfRichStringAbsStx.of_str('arg1'),
             ArgumentOfRichStringAbsStx.of_str('-arg2'),
             ],
        )
        utils.check__abs_stx(
            self,
            instruction_argument,
            utils.Arrangement(tcds_pop.empty()),
            utils.Expectation(
                path_ddv=self.configuration.path_ddv,
                expected_symbol_references=self.configuration.expected_symbol_references,
                source=has_remaining_part_of_first_line__re('arg1[ \t]+-arg2'),
                validation_result=self.configuration.validation_result,
            ),
        )


def configurations() -> Sequence[RelativityConfiguration]:
    all_except_rel_result = set(RelOptionType).difference({RelOptionType.REL_RESULT})

    for_non_default = [
        RelativityConfiguration(relativity_options.conf_rel_any(rel_option_type))
        for rel_option_type in all_except_rel_result
    ]
    return for_non_default + [
        RelativityConfiguration(relativity_options.default_conf_rel_any(RelOptionType.REL_HDS_CASE)),
    ]


def _python_executable(arguments: Sequence[ArgumentAbsStx] = ()) -> ProgramOfExecutableFileCommandLineAbsStx:
    return ProgramOfExecutableFileCommandLineAbsStx(
        PathStringAbsStx.of_shlex_quoted(sys.executable),
        arguments,
    )


class TestParseAbsolutePath(unittest.TestCase):
    def test_existing_file(self):
        arguments = _python_executable(
            [ArgumentOfRichStringAbsStx.of_str('remaining'),
             ArgumentOfRichStringAbsStx.of_str('args')]
        )
        expectation_on_exe_file = ExpectationOnExeFile(
            path_ddv=path_ddvs.absolute_file_name(sys.executable),
            expected_symbol_references=[],
        )

        validator_expectation = validation.Expectation.passes_all()

        self._check__abs_stx(
            arguments,
            expected_source_after_parse=has_remaining_part_of_first_line__re('remaining[ \t]+args'),
            expectation_on_exe_file=expectation_on_exe_file,
            validator_expectation=validator_expectation,
        )

    def test_non_existing_file(self):
        non_existing_file_path = non_existing_absolute_path('/this/file/is/assumed/to/not/exist')
        non_existing_file_path_str = str(non_existing_file_path)
        arguments = ProgramOfExecutableFileCommandLineAbsStx(
            PathStringAbsStx.of_plain_str(non_existing_file_path_str),
            [ArgumentOfRichStringAbsStx.of_str('remaining'),
             ArgumentOfRichStringAbsStx.of_str('args')]
        )

        expectation_on_exe_file = ExpectationOnExeFile(
            path_ddv=path_ddvs.absolute_file_name(non_existing_file_path_str),
            expected_symbol_references=[],
        )
        validator_expectation = validation.Expectation(passes_pre_sds=False,
                                                       passes_post_sds=True)

        self._check__abs_stx(
            arguments,
            expected_source_after_parse=has_remaining_part_of_first_line__re('remaining[ \t]+args'),
            expectation_on_exe_file=expectation_on_exe_file,
            validator_expectation=validator_expectation)

    def _check(self,
               arguments_str: str,
               expected_source_after_parse: Assertion[ParseSource],
               expectation_on_exe_file: ExpectationOnExeFile,
               validator_expectation: validation.Expectation):
        # ARRANGE #
        source = ParseSource(arguments_str)
        # ACT #
        exe_file = sut.parser().parse(source)
        # ASSERT #
        utils.check_exe_file(self, expectation_on_exe_file, exe_file)
        expected_source_after_parse.apply_with_message(self, source, 'parse source')
        exe_file_command = command_sdvs.for_executable_file(exe_file)
        with tcds_with_act_as_curr_dir() as environment:
            actual_validator = ddv_validators.all_of(exe_file_command.resolve(environment.symbols).validators)
            assertion = ddv_assertions.DdvValidationAssertion.of_expectation(validator_expectation,
                                                                             environment.tcds)
            assertion.apply_with_message(self, actual_validator, 'validation')

    def _check__abs_stx(self,
                        arguments: AbstractSyntax,
                        expected_source_after_parse: Assertion[ParseSource],
                        expectation_on_exe_file: ExpectationOnExeFile,
                        validator_expectation: validation.Expectation):
        for layout_spec in STANDARD_LAYOUT_SPECS:
            with self.subTest(layout_spec.name):
                self._check(
                    arguments.tokenization().layout(layout_spec.value),
                    expected_source_after_parse,
                    expectation_on_exe_file,
                    validator_expectation,
                )


def _parse_and_check(put: unittest.TestCase,
                     case: Case):
    # ARRANGE #
    source = ParseSource(case.source)
    # ACT #
    actual = sut.parser().parse(source)
    # ASSERT #
    utils.check_exe_file(put, case.expectation, actual)
    case.source_after_parse.apply_with_message(put, source,
                                               'parse source after parse')


def path_of(rel_option: RelOptionType,
            path_suffix: str) -> PathDdv:
    return path_ddvs.of_rel_option(rel_option, path_ddvs.constant_path_part(path_suffix))


def path_of_default_relativity(path_suffix: str) -> PathDdv:
    return path_ddvs.of_rel_option(syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF.options.default_option,
                                   path_ddvs.constant_path_part(path_suffix))


def has_remaining_part_of_first_line(remaining_part: str) -> Assertion[ParseSource]:
    return asrt_source.source_is_not_at_end(
        current_line_number=asrt.equals(1),
        remaining_part_of_current_line=asrt.equals(remaining_part),
    )


def has_remaining_part_of_first_line__re(remaining_part_reg_ex: str) -> Assertion[ParseSource]:
    return asrt_source.source_is_not_at_end(
        current_line_number=asrt.equals(1),
        remaining_part_of_current_line=asrt_str.matches_reg_ex(remaining_part_reg_ex),
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
