import functools
import pathlib
from pathlib import Path
from typing import List, Tuple, Callable

from exactly_lib.definitions.test_suite import section_names
from exactly_lib.processing import test_case_processing
from exactly_lib.processing.instruction_setup import TestCaseParsingSetup
from exactly_lib.processing.test_case_handling_setup import TestCaseHandlingSetup
from exactly_lib.section_document.model import SectionContents, ElementType, SectionContentElement
from exactly_lib.section_document.section_element_parsing import SectionElementParser
from exactly_lib.test_suite import structure
from exactly_lib.test_suite import test_suite_doc
from exactly_lib.test_suite.file_reading import exception, suite_file_reading
from exactly_lib.test_suite.instruction_set import instruction
from exactly_lib.test_suite.instruction_set.instruction import TestSuiteFileReferencesInstruction


class SuiteHierarchyReader:
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuiteHierarchy:
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

    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuiteHierarchy:
        return _SingleFileReader(self._environment, suite_file_path).apply()


class _SingleFileReader:
    def __init__(self,
                 environment: Environment,
                 root_suite_file_path: pathlib.Path):
        self.environment = environment
        self._root_suite_file_path = root_suite_file_path
        self._visited = {self._root_suite_file_path.resolve(): None}

    def apply(self) -> structure.TestSuiteHierarchy:
        return self.__call__([], self._root_suite_file_path)

    def __call__(self,
                 inclusions: List[pathlib.Path],
                 suite_file_path: pathlib.Path) -> structure.TestSuiteHierarchy:
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
        case_list = list(map(test_case_processing.test_case_reference_of_source_file, case_file_path_list))
        return structure.TestSuiteHierarchy(suite_file_path,
                                            inclusions,
                                            test_case_handling_setup,
                                            suite_list,
                                            case_list)

    def _resolve_paths(self,
                       test_suite: test_suite_doc.TestSuiteDocument,
                       suite_file_path: pathlib.Path) -> Tuple[List[Path], List[Path]]:

        def paths_for_instructions(env: instruction.Environment,
                                   section_name: str,
                                   section_contents: SectionContents,
                                   paths_checker: Callable[[SectionContentElement, List[Path]], None]
                                   ) -> List[Path]:
            ret_val = []
            for element in section_contents.elements:
                if element.element_type is ElementType.INSTRUCTION:
                    try:
                        path_instruction = element.instruction_info.instruction
                        assert isinstance(path_instruction, TestSuiteFileReferencesInstruction)
                        paths = path_instruction.resolve_paths(env)
                        paths_checker(element, paths)
                        ret_val.extend(paths)
                    except instruction.FileNotAccessibleSimpleError as ex:
                        raise exception.SuiteFileReferenceError(suite_file_path,
                                                                section_name,
                                                                element.source,
                                                                ex.file_path,
                                                                ex.error_message_header)
            return ret_val

        def check_suite_paths_for_double_inclusion(element: SectionContentElement,
                                                   paths_from_instruction: List[pathlib.Path]):
            for path in paths_from_instruction:
                resolved_path = path.resolve()
                if resolved_path in self._visited:
                    raise exception.SuiteDoubleInclusion(suite_file_path,
                                                         element.source,
                                                         path,
                                                         self._visited[resolved_path])
                else:
                    self._visited[resolved_path] = suite_file_path

        def no_check(element: SectionContentElement,
                     paths_from_instruction: List[pathlib.Path]):
            pass

        environment = instruction.Environment(suite_file_path.parent)
        return (paths_for_instructions(environment,
                                       section_names.SUITES.plain,
                                       test_suite.suites_section,
                                       check_suite_paths_for_double_inclusion),
                paths_for_instructions(environment,
                                       section_names.CASES.plain,
                                       test_suite.cases_section,
                                       no_check))
