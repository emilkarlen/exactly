import pathlib
import unittest

from exactly_lib.section_document import exceptions as sut
from exactly_lib_test.section_document.test_resources_test.source_location_assertions import \
    ARBITRARY_SOURCE_LOCATION_INFO
from exactly_lib_test.util.test_resources.line_source_assertions import ARBITRARY_LINE_SEQUENCE


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestVisitor)


class TestVisitor(unittest.TestCase):
    def test_visit_file_source_error(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        ex = sut.FileSourceError(ARBITRARY_LINE_SEQUENCE,
                                 'message',
                                 None,
                                 ARBITRARY_SOURCE_LOCATION_INFO)
        ret_val = ex.accept(visitor)
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_types,
                             [sut.FileSourceError],
                             'visited types')

    def test_visit_file_access_error(self):
        # ARRANGE #
        visitor = AVisitorThatRecordsVisitedMethods('ret-val')
        # ACT #
        ex = sut.FileAccessError(pathlib.Path(),
                                 'message',
                                 [])
        ret_val = ex.accept(visitor)
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_types,
                             [sut.FileAccessError],
                             'visited types')


class AVisitorThatRecordsVisitedMethods(sut.ParseErrorVisitor[str]):
    def __init__(self, ret_val: str):
        self._ret_val = ret_val
        self.visited_types = []

    def visit_file_source_error(self, ex: sut.FileSourceError) -> str:
        self.visited_types.append(sut.FileSourceError)
        return self._ret_val

    def visit_file_access_error(self, ex: sut.FileAccessError) -> str:
        self.visited_types.append(sut.FileAccessError)
        return self._ret_val
