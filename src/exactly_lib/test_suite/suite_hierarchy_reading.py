import functools
import pathlib

from exactly_lib.processing import test_case_processing
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.processing.test_case_processing import Preprocessor
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.section_document.parse import FileSourceError
from exactly_lib.test_suite import parser as test_suite_parser
from exactly_lib.test_suite.instruction_set import parse, instruction
from exactly_lib.test_suite.instruction_set.sections.configuration.instruction_definition import \
    ConfigurationSectionEnvironment
from exactly_lib.util import line_source
from . import structure
from . import test_suite_doc


class SuiteHierarchyReader:
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        """
        :raises SuiteReadError
        """
        raise NotImplementedError()


class Environment(tuple):
    def __new__(cls,
                preprocessor: Preprocessor,
                act_phase_setup: ActPhaseSetup):
        return tuple.__new__(cls, (preprocessor, act_phase_setup))

    @property
    def preprocessor(self) -> Preprocessor:
        return self[0]

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self[1]


class Reader(SuiteHierarchyReader):
    def __init__(self,
                 environment: Environment):
        self._environment = environment

    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        return _SingleFileReader(self._environment, suite_file_path).apply()


class _SingleFileReader:
    def __init__(self,
                 environment: Environment,
                 root_suite_file_path: pathlib.Path):
        self.environment = environment
        self._root_suite_file_path = root_suite_file_path.resolve()
        self._visited = {self._root_suite_file_path: None}

    def apply(self) -> structure.TestSuite:
        return self.__call__([], self._root_suite_file_path)

    def __call__(self,
                 inclusions: list,
                 suite_file_path: pathlib.Path) -> structure.TestSuite:
        source = line_source.new_for_file(suite_file_path)
        try:
            test_suite = test_suite_parser.Parser().apply(source)
        except FileSourceError as ex:
            raise parse.SuiteSyntaxError(suite_file_path,
                                         ex.source_error.line,
                                         ex.source_error.message,
                                         maybe_section_name=ex.maybe_section_name)
        configuration_section_environment = self._resolve_configuration_section_environment(test_suite)
        suite_file_path_list, case_file_path_list = self._resolve_paths(test_suite,
                                                                        suite_file_path)
        sub_inclusions = inclusions + [suite_file_path]
        sub_suites_reader = functools.partial(self, sub_inclusions)
        suite_list = list(map(sub_suites_reader, suite_file_path_list))
        case_list = list(map(test_case_processing.TestCaseSetup, case_file_path_list))
        return structure.TestSuite(suite_file_path,
                                   inclusions,
                                   TestCaseHandlingSetup(configuration_section_environment.act_phase_setup,
                                                         configuration_section_environment.preprocessor),
                                   suite_list,
                                   case_list)

    def _resolve_paths(self,
                       test_suite: test_suite_doc.TestSuiteDocument,
                       suite_file_path: pathlib.Path) -> (list, list):
        def paths_for_instructions(env: instruction.Environment,
                                   section_contents: SectionContents,
                                   check_visited: bool) -> list:
            ret_val = []
            for element in section_contents.elements:
                if element.element_type is ElementType.INSTRUCTION:
                    try:
                        paths = element.instruction.resolve_paths(env)
                        if check_visited:
                            for path in paths:
                                if path in self._visited:
                                    raise parse.SuiteDoubleInclusion(suite_file_path,
                                                                     element.first_line,
                                                                     path,
                                                                     self._visited[path])
                                else:
                                    self._visited[path] = suite_file_path
                        ret_val.extend(paths)
                    except instruction.FileNotAccessibleSimpleError as ex:
                        raise parse.SuiteFileReferenceError(suite_file_path,
                                                            element.first_line,
                                                            ex.file_path)
            return ret_val

        environment = instruction.Environment(suite_file_path.parent)
        return (paths_for_instructions(environment, test_suite.suites_section, True),
                paths_for_instructions(environment, test_suite.cases_section, False))

    def _resolve_configuration_section_environment(
            self,
            test_suite: test_suite_doc.TestSuiteDocument) -> ConfigurationSectionEnvironment:
        ret_val = ConfigurationSectionEnvironment(self.environment.preprocessor,
                                                  self.environment.act_phase_setup)
        for section_element in test_suite.configuration_section.elements:
            if section_element.element_type is ElementType.INSTRUCTION:
                section_element.instruction.execute(ret_val)
        return ret_val
