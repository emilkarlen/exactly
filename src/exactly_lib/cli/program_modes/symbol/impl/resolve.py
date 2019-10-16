from abc import ABC, abstractmethod
from typing import Tuple

from exactly_lib.cli.program_modes.test_suite.settings import TestSuiteExecutionSettings
from exactly_lib.execution.full_execution import execution as full_execution
from exactly_lib.execution.result import PhaseStepFailureException
from exactly_lib.processing import processors
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.standalone.accessor_resolver import AccessorResolver
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.actor import ActionToCheck


class Resolver(ABC):
    @abstractmethod
    def resolve(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        pass

    @staticmethod
    def _from_test_case(test_case: test_case_doc.TestCase,
                        conf_phase_configuration_builder: full_execution.ConfigurationBuilder,
                        ) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        mb_failure = full_execution.execute_configuration_phase(conf_phase_configuration_builder,
                                                                test_case.configuration_phase)
        if mb_failure is not None:
            raise PhaseStepFailureException(mb_failure)

        test_case_with_instructions = test_case.as_test_case_of_instructions()
        act_phase_instructions = [
            element.value
            for element in test_case_with_instructions.act_phase
        ]
        action_to_check = conf_phase_configuration_builder.actor.parse(act_phase_instructions)

        return (test_case_with_instructions,
                action_to_check)


class ResolverForTestSuite(Resolver):
    def __init__(self,
                 execution_settings: TestSuiteExecutionSettings,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 ):
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.execution_settings = execution_settings

    def resolve(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        from exactly_lib.test_suite.file_reading import suite_file_reading

        suite_doc = suite_file_reading.read_suite_document(self.execution_settings.suite_root_file_path,
                                                           self.suite_configuration_section_parser,
                                                           self.test_case_definition.parsing_setup)

        conf_env = suite_file_reading.derive_conf_section_environment(suite_doc,
                                                                      self.execution_settings.handling_setup)

        return self._from_test_case(
            suite_doc.case_phases,
            processors.default_conf_phase_configuration__of_file(
                self.execution_settings.suite_root_file_path,
                conf_env.act_phase_setup.actor,
            )
        )


class ResolverForTestCase(Resolver):
    def __init__(self,
                 execution_settings: TestCaseExecutionSettings,
                 test_case_definition: TestCaseDefinition,
                 suite_configuration_section_parser: SectionElementParser,
                 ):
        self.suite_configuration_section_parser = suite_configuration_section_parser
        self.test_case_definition = test_case_definition
        self.execution_settings = execution_settings

    def resolve(self) -> Tuple[test_case_doc.TestCaseOfInstructions, ActionToCheck]:
        accessor, act_phase_setup = self._accessor()
        test_case = accessor.apply(self._test_case_file_ref())

        return self._from_test_case(
            test_case,
            processors.default_conf_phase_configuration__of_home_dir(
                self.execution_settings.initial_home_dir_path,
                act_phase_setup.actor,
            )
        )

    def _accessor(self) -> Tuple[test_case_processing.Accessor, ActPhaseSetup]:
        case_execution_settings = self.execution_settings

        accessor_resolver = AccessorResolver(self.test_case_definition.parsing_setup,
                                             self.suite_configuration_section_parser,
                                             case_execution_settings.handling_setup)
        return accessor_resolver.resolve(case_execution_settings.test_case_file_path,
                                         case_execution_settings.run_as_part_of_explicit_suite)

    def _test_case_file_ref(self) -> test_case_processing.TestCaseFileReference:
        return test_case_processing.test_case_reference_of_source_file(
            self.execution_settings.test_case_file_path)
