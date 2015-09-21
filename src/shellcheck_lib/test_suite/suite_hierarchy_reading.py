import pathlib
import functools

from shellcheck_lib.document.model import PhaseContents, ElementType
from shellcheck_lib.document.parse import SourceError
from shellcheck_lib.general import line_source
from shellcheck_lib.test_case import test_case_processing
from . import test_suite_doc
from . import structure
from shellcheck_lib.test_case.preprocessor import IdentityPreprocessor
from shellcheck_lib.test_suite.instruction_set import parse, instruction
from shellcheck_lib.test_suite.instruction_set.sections.anonymous import AnonymousSectionEnvironment
import shellcheck_lib.test_suite.parser


class SuiteHierarchyReader:
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        """
        :raises SuiteReadError
        """
        raise NotImplementedError()


class Reader(SuiteHierarchyReader):
    def apply(self, suite_file_path: pathlib.Path) -> structure.TestSuite:
        return _SingleFileReader(suite_file_path).apply()


class _SingleFileReader:
    def __init__(self, root_suite_file_path: pathlib.Path):
        self._root_suite_file_path = root_suite_file_path.resolve()
        self._visited = {self._root_suite_file_path: None}

    def apply(self) -> structure.TestSuite:
        return self.__call__([], self._root_suite_file_path)

    def __call__(self,
                 inclusions: list,
                 suite_file_path: pathlib.Path) -> structure.TestSuite:
        source = line_source.new_for_file(suite_file_path)
        try:
            test_suite = shellcheck_lib.test_suite.parser.PARSER.apply(source)
        except SourceError as ex:
            raise parse.SuiteSyntaxError(suite_file_path,
                                         ex.line,
                                         ex.message)
        anonymous_section_environment = self._resolve_preprocessor(test_suite)
        suite_file_path_list, case_file_path_list = self._resolve_paths(test_suite,
                                                                        suite_file_path)
        sub_inclusions = inclusions + [suite_file_path]
        sub_suites_reader = functools.partial(self, sub_inclusions)
        suite_list = list(map(sub_suites_reader, suite_file_path_list))
        case_list = list(map(test_case_processing.TestCaseSetup, case_file_path_list))
        return structure.TestSuite(suite_file_path,
                                   inclusions,
                                   anonymous_section_environment.preprocessor,
                                   suite_list,
                                   case_list)

    def _resolve_paths(self,
                       test_suite: test_suite_doc.TestSuiteDocument,
                       suite_file_path: pathlib.Path) -> (list, list):
        def paths_for_instructions(env: instruction.Environment,
                                   section_contents: PhaseContents,
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

    @staticmethod
    def _resolve_preprocessor(test_suite: test_suite_doc.TestSuiteDocument) -> AnonymousSectionEnvironment:
        ret_val = AnonymousSectionEnvironment(IdentityPreprocessor())
        for section_element in test_suite.anonymous_section.elements:
            if section_element.element_type is ElementType.INSTRUCTION:
                section_element.instruction.execute(ret_val)
        return ret_val
