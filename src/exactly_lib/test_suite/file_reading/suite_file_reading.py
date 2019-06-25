import pathlib
from typing import Tuple

from exactly_lib.definitions.test_suite import section_names_plain
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup, InstructionsSetup
from exactly_lib.processing.parse.test_case_parser import SectionParserConstructorForParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup, ComposedTestCaseTransformer, \
    TestCaseTransformer
from exactly_lib.section_document import document_parsers
from exactly_lib.section_document import exceptions
from exactly_lib.section_document import section_parsing
from exactly_lib.section_document.element_parsers.section_element_parsers import ParserFromSequenceOfParsers
from exactly_lib.section_document.model import ElementType, SectionContents
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case.test_case_doc import TestCase
from exactly_lib.test_suite import test_suite_doc
from exactly_lib.test_suite.file_reading import exception
from exactly_lib.test_suite.instruction_set.sections import cases
from exactly_lib.test_suite.instruction_set.sections import suites
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment, ConfigurationSectionInstruction


def read_suite_document(suite_file_path: pathlib.Path,
                        configuration_section_parser: SectionElementParser,
                        test_case_parsing_setup: TestCaseParsingSetup,
                        ) -> test_suite_doc.TestSuiteDocument:
    """
    :raises exception.SuiteParseError: The suite file has an error related to parsing
    """
    parser = _Parser(configuration_section_parser,
                     test_case_parsing_setup)
    try:
        return parser.apply(suite_file_path)
    except exceptions.ParseError as ex:
        raise exception.SuiteParseError(suite_file_path, ex)


def resolve_test_case_handling_setup(
        test_suite: test_suite_doc.TestSuiteDocument,
        default_handling_setup: TestCaseHandlingSetup) -> TestCaseHandlingSetup:
    instruction_environment = derive_conf_section_environment(test_suite, default_handling_setup)
    transformer_that_adds_instr_from_suite = _TestCaseInstructionsFromTestSuiteAdder(test_suite)
    return TestCaseHandlingSetup(instruction_environment.act_phase_setup,
                                 instruction_environment.preprocessor,
                                 ComposedTestCaseTransformer(default_handling_setup.transformer,
                                                             transformer_that_adds_instr_from_suite))


def derive_conf_section_environment(test_suite: test_suite_doc.TestSuiteDocument,
                                    default_handling_setup: TestCaseHandlingSetup
                                    ) -> ConfigurationSectionEnvironment:
    instruction_environment = ConfigurationSectionEnvironment(default_handling_setup.preprocessor,
                                                              default_handling_setup.act_phase_setup)
    for section_element in test_suite.configuration_section.elements:
        if section_element.element_type is ElementType.INSTRUCTION:
            instruction = section_element.instruction_info.instruction
            assert isinstance(instruction, ConfigurationSectionInstruction)
            instruction.execute(instruction_environment)
    return instruction_environment


class _Parser:
    def __init__(self,
                 configuration_section_parser: SectionElementParser,
                 test_case_parsing_setup: TestCaseParsingSetup):
        phase_parser_constructor = SectionParserConstructorForParsingSetup(test_case_parsing_setup)
        parser_configuration = section_parsing.SectionsConfiguration(
            (
                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CONF,
                    ParserFromSequenceOfParsers(
                        (
                            configuration_section_parser,
                            phase_parser_constructor.of(InstructionsSetup.config_instruction_set.fget)
                        ),
                    )),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__SUITS,
                    suites.new_parser()),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASES,
                    cases.new_parser()),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASE_SETUP,
                    phase_parser_constructor.of(InstructionsSetup.setup_instruction_set.fget)),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASE_ACT,
                    test_case_parsing_setup.act_phase_parser),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASE_BEFORE_ASSERT,
                    phase_parser_constructor.of(InstructionsSetup.before_assert_instruction_set.fget)),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASE_ASSERT,
                    phase_parser_constructor.of(InstructionsSetup.assert_instruction_set.fget)),

                section_parsing.SectionConfiguration(
                    section_names_plain.SECTION_NAME__CASE_CLEANUP,
                    phase_parser_constructor.of(InstructionsSetup.cleanup_instruction_set.fget)),
            ),
            default_section_name=section_names_plain.DEFAULT_SECTION_NAME
        )
        self.__section_doc_parser = document_parsers.new_parser_for(parser_configuration)

    def apply(self, suite_file_path: pathlib.Path) -> test_suite_doc.TestSuiteDocument:
        document = self.__section_doc_parser.parse_file(suite_file_path)

        suite_conf, case_conf = _separate_configuration_elements(
            document.elements_for_section_or_empty_if_phase_not_present(section_names_plain.SECTION_NAME__CONF)
        )
        return test_suite_doc.TestSuiteDocument(
            suite_conf,
            document.elements_for_section_or_empty_if_phase_not_present(section_names_plain.SECTION_NAME__SUITS),
            document.elements_for_section_or_empty_if_phase_not_present(section_names_plain.SECTION_NAME__CASES),
            TestCase(
                case_conf,
                document.elements_for_section_or_empty_if_phase_not_present(
                    section_names_plain.SECTION_NAME__CASE_SETUP),
                document.elements_for_section_or_empty_if_phase_not_present(
                    section_names_plain.SECTION_NAME__CASE_ACT),
                document.elements_for_section_or_empty_if_phase_not_present(
                    section_names_plain.SECTION_NAME__CASE_BEFORE_ASSERT),
                document.elements_for_section_or_empty_if_phase_not_present(
                    section_names_plain.SECTION_NAME__CASE_ASSERT),
                document.elements_for_section_or_empty_if_phase_not_present(
                    section_names_plain.SECTION_NAME__CASE_CLEANUP),
            ),
        )


def resolve_handling_setup_from_suite_file(default_handling_setup: TestCaseHandlingSetup,
                                           configuration_section_parser: SectionElementParser,
                                           test_case_parsing_setup: TestCaseParsingSetup,
                                           suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    suite_document = read_suite_document(suite_to_read_config_from,
                                         configuration_section_parser,
                                         test_case_parsing_setup)
    return resolve_test_case_handling_setup(suite_document,
                                            default_handling_setup)


def _separate_configuration_elements(section_contents: SectionContents
                                     ) -> Tuple[SectionContents, SectionContents]:
    suite_elements = []
    case_elements = []

    for element in section_contents.elements:
        if element.element_type is ElementType.INSTRUCTION:
            if isinstance(element.instruction_info.instruction, ConfigurationSectionInstruction):
                suite_elements.append(element)
            else:
                case_elements.append(element)
        else:
            suite_elements.append(element)

    return SectionContents(tuple(suite_elements)), SectionContents(tuple(case_elements))


class _TestCaseInstructionsFromTestSuiteAdder(TestCaseTransformer):
    def __init__(self, test_suite: test_suite_doc.TestSuiteDocument):
        self._test_suite = test_suite

    def transform(self, test_case: TestCase) -> TestCase:
        def append(fst: SectionContents, snd: SectionContents) -> SectionContents:
            return SectionContents(tuple(list(fst.elements) + list(snd.elements)))

        test_suite = self._test_suite.case_phases

        return TestCase(
            configuration_phase=append(test_suite.configuration_phase, test_case.configuration_phase),
            setup_phase=append(test_suite.setup_phase, test_case.setup_phase),
            act_phase=append(test_suite.act_phase, test_case.act_phase),
            before_assert_phase=append(test_suite.before_assert_phase, test_case.before_assert_phase),
            assert_phase=append(test_suite.assert_phase, test_case.assert_phase),
            cleanup_phase=append(test_case.cleanup_phase, test_suite.cleanup_phase),
        )
