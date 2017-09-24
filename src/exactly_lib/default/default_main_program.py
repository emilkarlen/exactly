import datetime

from exactly_lib import program_info
from exactly_lib.cli import main_program
from exactly_lib.cli.program_modes.test_case import execution as test_case_execution
from exactly_lib.cli.program_modes.test_case.settings import TestCaseExecutionSettings
from exactly_lib.execution.full_execution import PredefinedProperties
from exactly_lib.help.builtin.contents_structure import BuiltinSymbolDocumentation
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.processing.processors import TestCaseDefinition
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.symbol.resolver_structure import SymbolValueResolver, container_of_builtin
from exactly_lib.test_suite.instruction_set.test_suite_definition import TestSuiteDefinition
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.util.textformat.structure.document import SectionContents


class BuiltinSymbol:
    def __init__(self,
                 name: str,
                 resolver: SymbolValueResolver,
                 single_line_description: str,
                 documentation: SectionContents,
                 ):
        self._name = name
        self._resolver = resolver
        self._single_line_description = single_line_description
        self._documentation = documentation

    @property
    def name(self) -> str:
        return self._name

    @property
    def as_name_and_container_pair(self):
        return self._name, container_of_builtin(self._resolver)

    @property
    def resolver(self) -> SymbolValueResolver:
        return self._resolver

    @property
    def documentation(self) -> BuiltinSymbolDocumentation:
        return BuiltinSymbolDocumentation(self._resolver.value_type, self.name,
                                          self._single_line_description,
                                          self._documentation)


class TestCaseDefinitionForMainProgram:
    """
    Corresponds to TestCaseDefinition, but with
    extra information about predefined symbols for the help system.
    """

    #  TODO: Should act phase parser be part of this class?
    # Feels right, but have not looked into it.

    def __init__(self,
                 instruction_name_extractor_function,
                 instruction_setup: InstructionsSetup,
                 builtin_symbols: list):
        """
        :param builtin_symbols: [`BuiltinSymbol`]
        """
        self.instruction_setup = instruction_setup
        self.instruction_name_extractor_function = instruction_name_extractor_function
        self.builtin_symbols = builtin_symbols


class MainProgram(main_program.MainProgram):
    def __init__(self,
                 output: StdOutputFiles,
                 test_case_definition: TestCaseDefinitionForMainProgram,
                 test_suite_definition: TestSuiteDefinition,
                 default: TestCaseHandlingSetup):
        super().__init__(output,
                         test_case_definition.instruction_setup,
                         test_suite_definition.configuration_section_instructions,
                         default,
                         [builtin_symbol.documentation
                          for builtin_symbol in test_case_definition.builtin_symbols
                          ]
                         )
        self._test_case_definition = TestCaseDefinition(
            test_case_definition.instruction_name_extractor_function,
            test_case_definition.instruction_setup,
            PredefinedProperties(
                SymbolTable(dict(map(BuiltinSymbol.as_name_and_container_pair.fget,
                                     test_case_definition.builtin_symbols)))
            )
        )
        self._test_suite_definition = test_suite_definition

    def execute_test_case(self, settings: TestCaseExecutionSettings) -> int:
        return test_case_execution.execute(self._std,
                                           self._test_case_definition,
                                           self._test_suite_definition.configuration_section_parser,
                                           settings)

    def execute_test_suite(self, test_suite_execution_settings) -> int:
        from exactly_lib.processing import processors
        from exactly_lib.test_suite import enumeration
        from exactly_lib.test_suite import suite_hierarchy_reading
        from exactly_lib.test_suite import execution
        default_configuration = processors.Configuration(self._test_case_definition,
                                                         test_suite_execution_settings.handling_setup,
                                                         False,
                                                         self._sds_root_name_prefix_for_suite())
        executor = execution.Executor(default_configuration,
                                      self._output,
                                      suite_hierarchy_reading.Reader(
                                          suite_hierarchy_reading.Environment(
                                              self._test_suite_definition.configuration_section_parser,
                                              default_configuration.default_handling_setup)
                                      ),
                                      test_suite_execution_settings.reporter_factory,
                                      enumeration.DepthFirstEnumerator(),
                                      processors.new_processor_that_should_not_pollute_current_process,
                                      test_suite_execution_settings.suite_root_file_path)
        return executor.execute()

    @staticmethod
    def _sds_root_name_prefix_for_suite():
        today = datetime.datetime.today()
        datetime_suffix = today.strftime('%Y-%m-%d-%H-%M-%S')
        sandbox_directory_root_name_prefix = program_info.PROGRAM_NAME + '-suite-' + datetime_suffix + '-'
        return sandbox_directory_root_name_prefix
