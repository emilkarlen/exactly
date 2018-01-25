import pathlib

from exactly_lib.help_texts.test_suite.section_names import SECTION_NAME__CONF, SECTION_NAME__SUITS, \
    SECTION_NAME__CASES, \
    DEFAULT_SECTION_NAME, SECTION_NAME__CASE_SETUP
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup, ComposedTestCaseTransformer
from exactly_lib.section_document import document_parser
from exactly_lib.section_document.exceptions import FileSourceError
from exactly_lib.section_document.model import ElementType
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.utils import new_for_file
from exactly_lib.test_suite import case_instructions
from exactly_lib.test_suite import test_suite_doc
from exactly_lib.test_suite.case_instructions import TestSuiteInstructionsForCaseSetup
from exactly_lib.test_suite.instruction_set import parse
from exactly_lib.test_suite.instruction_set.sections import cases
from exactly_lib.test_suite.instruction_set.sections import suites
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment, ConfigurationSectionInstruction
from exactly_lib.test_suite.test_suite_doc import TestCaseInstructionSetupFromSuite


def read_suite_document(suite_file_path: pathlib.Path,
                        configuration_section_parser: document_parser.SectionElementParser,
                        test_case_parsing_setup: TestCaseParsingSetup,
                        ) -> test_suite_doc.TestSuiteDocument:
    """
    :raises parse.SuiteSyntaxError: The suite file has syntax errors
    """
    source = new_for_file(suite_file_path)
    file_inclusion_relativity_root = suite_file_path.parent
    parser = _Parser(configuration_section_parser,
                     test_case_parsing_setup)
    try:
        return parser.apply(suite_file_path,
                            file_inclusion_relativity_root,
                            source)
    except FileSourceError as ex:
        raise parse.SuiteSyntaxError(suite_file_path,
                                     ex.source_error.source,
                                     ex.source_error.message,
                                     maybe_section_name=ex.maybe_section_name)


def resolve_test_case_handling_setup(
        test_suite: test_suite_doc.TestSuiteDocument,
        default_handling_setup: TestCaseHandlingSetup) -> TestCaseHandlingSetup:
    instruction_environment = _derive_conf_section_environment(test_suite, default_handling_setup)
    transformer_that_adds_instr_from_suite = TestSuiteInstructionsForCaseSetup(test_suite.case_setup.setup_section)
    return TestCaseHandlingSetup(instruction_environment.act_phase_setup,
                                 instruction_environment.preprocessor,
                                 ComposedTestCaseTransformer(default_handling_setup.transformer,
                                                             transformer_that_adds_instr_from_suite))


def _derive_conf_section_environment(test_suite: test_suite_doc.TestSuiteDocument,
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
                 configuration_section_parser: document_parser.SectionElementParser,
                 test_case_parsing_setup: TestCaseParsingSetup):
        parser_configuration = document_parser.SectionsConfiguration(
            (
                document_parser.SectionConfiguration(SECTION_NAME__CONF,
                                                     configuration_section_parser),
                document_parser.SectionConfiguration(SECTION_NAME__SUITS, suites.new_parser()),
                document_parser.SectionConfiguration(SECTION_NAME__CASES, cases.new_parser()),
                document_parser.SectionConfiguration(SECTION_NAME__CASE_SETUP,
                                                     case_instructions.new_setup_phase_parser(test_case_parsing_setup)),
            ),
            default_section_name=DEFAULT_SECTION_NAME
        )
        self.__section_doc_parser = document_parser.new_parser_for(parser_configuration)

    def apply(self,
              suite_file_path: pathlib.Path,
              file_inclusion_relativity_root: pathlib.Path,
              suite_file_source: ParseSource) -> test_suite_doc.TestSuiteDocument:
        document = self.__section_doc_parser.parse(suite_file_path,
                                                   file_inclusion_relativity_root,
                                                   suite_file_source)
        return test_suite_doc.TestSuiteDocument(
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CONF),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CASES),
            TestCaseInstructionSetupFromSuite(
                document.elements_for_section_or_empty_if_phase_not_present(SECTION_NAME__CASE_SETUP)),
        )


def resolve_handling_setup_from_suite_file(default_handling_setup: TestCaseHandlingSetup,
                                           configuration_section_parser: document_parser.SectionElementParser,
                                           test_case_parsing_setup: TestCaseParsingSetup,
                                           suite_to_read_config_from: pathlib.Path) -> TestCaseHandlingSetup:
    suite_document = read_suite_document(suite_to_read_config_from,
                                         configuration_section_parser,
                                         test_case_parsing_setup)
    return resolve_test_case_handling_setup(suite_document,
                                            default_handling_setup)
