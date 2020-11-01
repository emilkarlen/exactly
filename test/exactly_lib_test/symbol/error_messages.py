import unittest
from pathlib import Path

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.err_msg import error_messages as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.section_document.test_resources.source_elements import \
    SOURCE_LOCATION_PATH_WITH_INCLUSIONS_AND_FILE_NAMES
from exactly_lib_test.symbol.test_resources.reference_restrictions import UnconditionallyValidReferenceRestrictions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefinedAtLines),
        unittest.makeSuite(TestDuplicateDefinition),
        unittest.makeSuite(TestUndefinedSymbol),
    ])


_IS_ANY_TEXT = asrt_text_doc.is_any_text()


class TestDefinedAtLines(unittest.TestCase):
    def test_builtin(self):
        # ACT #
        actual = sut.defined_at_line__err_msg_lines(None)
        # ASSERT #
        is_list_of_strings = asrt.is_sequence_of(asrt.is_instance(str))

        is_list_of_strings.apply_without_message(self, actual)

    def test_user_defined(self):
        # ARRANGE #
        sli = SourceLocationInfo(Path.cwd(),
                                 SOURCE_LOCATION_PATH_WITH_INCLUSIONS_AND_FILE_NAMES)
        # ACT #
        actual = sut.defined_at_line__err_msg_lines(sli)
        # ASSERT #
        is_list_of_strings = asrt.is_sequence_of(asrt.is_instance(str))

        is_list_of_strings.apply_without_message(self, actual)


class TestDuplicateDefinition(unittest.TestCase):
    def test_clash_with_builtin(self):
        actual = sut.duplicate_symbol_definition(None,
                                                 'the_symbol_name')
        _IS_ANY_TEXT.apply_without_message(self, actual)

    def test_clash_with_user_defined(self):
        sli = SourceLocationInfo(Path.cwd(),
                                 SOURCE_LOCATION_PATH_WITH_INCLUSIONS_AND_FILE_NAMES)
        actual = sut.duplicate_symbol_definition(sli,
                                                 'the_symbol_name')

        _IS_ANY_TEXT.apply_without_message(self, actual)


class TestUndefinedSymbol(unittest.TestCase):
    def test(self):
        actual = sut.undefined_symbol(SymbolReference('the_symbol_name',
                                                      UnconditionallyValidReferenceRestrictions()))

        _IS_ANY_TEXT.apply_without_message(self, actual)
