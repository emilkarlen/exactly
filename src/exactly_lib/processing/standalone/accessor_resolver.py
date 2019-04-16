import pathlib
from typing import Optional, Tuple

from exactly_lib.definitions.test_suite import file_names
from exactly_lib.processing import test_case_processing as processing, processors
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.section_element_parsing import SectionElementParser


class AccessorResolver:
    def __init__(self,
                 test_case_parsing_setup: TestCaseParsingSetup,
                 suite_configuration_section_parser: SectionElementParser,
                 default_handling_setup: TestCaseHandlingSetup):
        self._test_case_parsing_setup = test_case_parsing_setup
        self._suite_configuration_section_parser = suite_configuration_section_parser
        self._default_handling_setup = default_handling_setup

    def resolve(self,
                test_case_file_path: pathlib.Path,
                explicit_suite_file_path: Optional[pathlib.Path]
                ) -> Tuple[processing.Accessor, ActPhaseSetup]:
        """
        :raises SuiteParseError
        """
        handling_setup = self._handling_setup(test_case_file_path,
                                              explicit_suite_file_path)
        return (processors.new_accessor(handling_setup.preprocessor,
                                        self._test_case_parsing_setup,
                                        handling_setup.transformer),
                handling_setup.act_phase_setup,
                )

    def _handling_setup(self,
                        test_case_file_path: pathlib.Path,
                        explicit_suite_file_path: Optional[pathlib.Path]
                        ) -> TestCaseHandlingSetup:
        """
        :raises SuiteParseError
        """

        def get_suite_file() -> Optional[pathlib.Path]:
            if explicit_suite_file_path:
                return explicit_suite_file_path

            default_suite_file_path = test_case_file_path.parent / file_names.DEFAULT_SUITE_FILE
            if default_suite_file_path.is_file():
                return default_suite_file_path

            return None

        suite_file_path = get_suite_file()

        if not suite_file_path:
            return self._default_handling_setup
        from exactly_lib.test_suite.file_reading.suite_file_reading import resolve_handling_setup_from_suite_file
        return resolve_handling_setup_from_suite_file(self._default_handling_setup,
                                                      self._suite_configuration_section_parser,
                                                      self._test_case_parsing_setup,
                                                      suite_file_path)
