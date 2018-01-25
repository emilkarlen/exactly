import functools
import pathlib

from exactly_lib.processing import test_case_processing
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.document_parser import SectionElementParser
from exactly_lib.section_document.model import SectionContents, ElementType
from exactly_lib.test_suite.instruction_set import parse, instruction
from . import structure
from . import suite_file_reading
from . import test_suite_doc


class SuiteHierarchyReader:
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        """
        :raises SuiteReadError
        """
        raise NotImplementedError()


class Environment(tuple):
    def __new__(cls,
                configuration_section_parser: SectionElementParser,
                test_case_parsing_setup: TestCaseParsingSetup,
                default_test_case_handling_setup: TestCaseHandlingSetup):
        return tuple.__new__(cls, (configuration_section_parser,
                                   default_test_case_handling_setup,
                                   test_case_parsing_setup))

    @property
    def configuration_section_parser(self) -> SectionElementParser:
        return self[0]

    @property
    def default_test_case_handling_setup(self) -> TestCaseHandlingSetup:
        return self[1]

    @property
    def test_case_parsing_setup(self) -> TestCaseParsingSetup:
        return self[2]


class Reader(SuiteHierarchyReader):
    def __init__(self, environment: Environment):
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
        test_suite = suite_file_reading.read_suite_document(suite_file_path,
                                                            self.environment.configuration_section_parser,
                                                            self.environment.test_case_parsing_setup)
        test_case_handling_setup = suite_file_reading.resolve_test_case_handling_setup(
            test_suite,
            self.environment.default_test_case_handling_setup)

        suite_file_path_list, case_file_path_list = self._resolve_paths(test_suite,
                                                                        suite_file_path)
        sub_inclusions = inclusions + [suite_file_path]
        sub_suites_reader = functools.partial(self, sub_inclusions)
        suite_list = list(map(sub_suites_reader, suite_file_path_list))
        case_list = list(map(test_case_processing.test_case_setup_of_source_file, case_file_path_list))
        return structure.TestSuite(suite_file_path,
                                   inclusions,
                                   test_case_handling_setup,
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
                        paths = element.instruction_info.instruction.resolve_paths(env)
                        if check_visited:
                            for path in paths:
                                if path in self._visited:
                                    raise parse.SuiteDoubleInclusion(suite_file_path,
                                                                     element.source,
                                                                     path,
                                                                     self._visited[path])
                                else:
                                    self._visited[path] = suite_file_path
                        ret_val.extend(paths)
                    except instruction.FileNotAccessibleSimpleError as ex:
                        raise parse.SuiteFileReferenceError(suite_file_path,
                                                            element.source,
                                                            ex.file_path)
            return ret_val

        environment = instruction.Environment(suite_file_path.parent)
        return (paths_for_instructions(environment, test_suite.suites_section, True),
                paths_for_instructions(environment, test_suite.cases_section, False))
