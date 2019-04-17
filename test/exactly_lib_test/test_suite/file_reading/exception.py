import pathlib
import unittest
from typing import Optional

from exactly_lib.section_document import exceptions as sec_doc_exceptions
from exactly_lib.section_document.source_location import SourceLocationPath
from exactly_lib.test_suite.file_reading import exception as sut
from exactly_lib_test.util.test_resources.line_source_assertions import ARBITRARY_LINE_SEQUENCE


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def test_visit_parse_error(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        ex = sut.SuiteParseError(pathlib.Path('a path'),
                                 sec_doc_exceptions.FileAccessError(pathlib.Path(),
                                                                    'message',
                                                                    []))
        ret_val = visitor.visit(ex)
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_types,
                             [sut.SuiteParseError],
                             'visited types')

    def test_visit_double_inclusion_error(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        ex = sut.SuiteDoubleInclusion(pathlib.Path('a path'),
                                      ARBITRARY_LINE_SEQUENCE,
                                      pathlib.Path('included suite file'),
                                      pathlib.Path('first_referenced_from'))
        ret_val = visitor.visit(ex)
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_types,
                             [sut.SuiteDoubleInclusion],
                             'visited types')

    def test_visit_file_reference_error(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        ex = sut.SuiteFileReferenceError(pathlib.Path('suite file'),
                                         'section name',
                                         ARBITRARY_LINE_SEQUENCE,
                                         pathlib.Path('reference'),
                                         'error_message_header')
        ret_val = visitor.visit(ex)
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_types,
                             [sut.SuiteFileReferenceError],
                             'visited types')

    def test_visit_unknown_type(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(InvalidSuiteReadErrorClass())
        # ASSERT #
        self.assertIsNot(visitor.visited_types,
                         'No visit method should have been executed.')


class AVisitorThatRecordsVisitedMethods(sut.SuiteReadErrorVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_parse_error(self, ex: sut.SuiteParseError) -> str:
        self.visited_types.append(sut.SuiteParseError)
        return self._ret_val

    def visit_double_inclusion_error(self, ex: sut.SuiteDoubleInclusion) -> str:
        self.visited_types.append(sut.SuiteDoubleInclusion)
        return self._ret_val

    def visit_file_reference_error(self, ex: sut.SuiteFileReferenceError) -> str:
        self.visited_types.append(sut.SuiteFileReferenceError)
        return self._ret_val


class InvalidSuiteReadErrorClass(sut.SuiteReadError):
    def __init__(self):
        super().__init__(pathlib.Path('a path'), None)

    @property
    def source_location(self) -> Optional[SourceLocationPath]:
        raise NotImplementedError('not used')
