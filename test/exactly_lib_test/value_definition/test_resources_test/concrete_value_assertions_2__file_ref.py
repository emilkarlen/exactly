import unittest

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, NoRestriction, \
    EitherStringOrFileRefRelativityRestriction, StringRestriction
from exactly_lib.value_definition.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import FileRefTestImpl
from exactly_lib_test.test_case_file_structure.test_resources_test.file_ref import FileRefWithValRefInRootPartTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import concrete_value_assertions_2 as sut
from exactly_lib_test.value_definition.test_resources.value_definition_utils import \
    symbol_table_with_single_string_value, symbol_table_from_value_definitions, string_value_definition, \
    file_ref_value_definition, symbol_table_with_single_file_ref_value
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_references


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEqualsCommonToBothAssertionMethods(),
        TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_PathSuffixAsNothing),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
        unittest.makeSuite(Test2NotEquals),
    ])


class TestEqualsCommonToBothAssertionMethods(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('file-name')),
             empty_symbol_table(),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsFixedPath('a-file-name')),
             empty_symbol_table(),
             ),
            ('symbol-ref/NOT Exists pre SDS/fixed path suffix',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('reffed-name',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
            ('symbol-ref(either-string-or-file-ref actual is file-ref)/NOT Exists pre SDS/fixed path suffix',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('reffed-name',
                                EitherStringOrFileRefRelativityRestriction(
                                    StringRestriction(),
                                    _relativity_restriction({RelOptionType.REL_ACT}, False))
                                ),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
            ('symbol-ref(either-string-or-file-ref actual is string)/NOT Exists pre SDS/fixed path suffix',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('reffed-name',
                                EitherStringOrFileRefRelativityRestriction(
                                    StringRestriction(),
                                    _relativity_restriction({RelOptionType.REL_ACT}, False))
                                ),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
            ('Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             symbol_table_with_single_string_value('symbol-name', 'value'),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             symbol_table_with_single_string_value('a-symbol-name', 'value'),
             ),
            ('symbol-ref/NOT Exists pre SDS/no path suffix',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('reffed-name',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsNothing()),
             symbol_table_from_value_definitions([
                 string_value_definition('symbol-name', 'string-value'),
                 file_ref_value_definition('reffed-name')]),
             ),
        ]
        for test_case_name, file_ref, symbol_table_for_method2 in test_cases:
            assert isinstance(file_ref, FileRef), 'Type info for IDE'
            value = FileRefConstant(file_ref)
            with self.subTest(msg='file_ref_equals::' + test_case_name):
                assertion = sut.file_ref_resolver_equals(value)
                assertion.apply_with_message(self, value, test_case_name)
            with self.subTest(msg='equals_file_ref2::' + test_case_name):
                assertion = sut.equals_file_ref_resolver2(file_ref,
                                                          equals_value_references(value.references),
                                                          symbol_table_for_method2)
                assertion.apply_with_message(self, value, test_case_name)


class TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Different symbol references in path suffixes',
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             PathPartAsNothing()),
             symbol_table_from_value_definitions([
                 string_value_definition('path_suffix_symbol_1', 'suffix-file-name'),
                 string_value_definition('path_suffix_symbol_2', 'suffix-file-name'),
             ])
             ),
            ('Different symbol references in root',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('path_root_symbol_1',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('path_root_symbol_2',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             symbol_table_from_value_definitions([
                 file_ref_value_definition('path_root_symbol_1',
                                           FileRefTestImpl(RelOptionType.REL_TMP,
                                                           PathPartAsFixedPath('suffix-of-root'))),
                 file_ref_value_definition('path_root_symbol_2',
                                           FileRefTestImpl(RelOptionType.REL_TMP,
                                                           PathPartAsFixedPath('suffix-of-root'))
                                           ),
             ])
             ),
            ('Different kind of root resolving',
             FileRefWithValRefInRootPartTestImpl(
                 ValueReference('reffed_file_ref_name',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('2')),
             FileRefTestImpl(RelOptionType.REL_ACT,
                             PathPartAsFixedPath('1/2')),
             symbol_table_with_single_file_ref_value('reffed_file_ref_name',
                                                     FileRefTestImpl(RelOptionType.REL_ACT,
                                                                     PathPartAsFixedPath('1'))),
             ),
        ]
        for test_case_name, first, second, symbol_table_for_method2 in test_cases:
            assert isinstance(first, FileRef), 'Type info for IDE (first)'
            assert isinstance(second, FileRef), 'Type info for IDE (second)'
            first_value = FileRefConstant(first)
            second_value = FileRefConstant(second)
            with self.subTest(msg='1::' + test_case_name):
                assertion = sut.equals_file_ref_resolver2(first,
                                                          asrt.ignore,
                                                          symbol_table_for_method2)
                assertion.apply_with_message(self, second_value, test_case_name)
            with self.subTest(msg='2::' + test_case_name):
                assertion = sut.equals_file_ref_resolver2(second,
                                                          asrt.ignore,
                                                          symbol_table_for_method2)
                assertion.apply_with_message(self, first_value, test_case_name)


class TestNotEquals_PathSuffixAsFixedPath(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__differs__relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsFixedPath('file-name'))
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_HOME},
                                                                                            False)),
                                                     PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__differs__value_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsFixedPath('file-name'))
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('OTHER-reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_ACT},
                                                                                            False)),
                                                     PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_RESULT,
                                 PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_RESULT,
                                   PathPartAsFixedPath('file-name'))
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_ACT},
                                                                                            False)),
                                                     PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsFixedPath('file-name'))
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    NoRestriction()),
                                                     PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')


class TestNotEquals_PathSuffixAsNothing(unittest.TestCase):
    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                                   PathPartAsNothing())
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                                 PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT,
                                   PathPartAsNothing())
        actual = FileRefTestImpl(RelOptionType.REL_HOME,
                                 PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__differs__relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsNothing())
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_HOME},
                                                                                            False)),
                                                     PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__differs__value_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsNothing())
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('OTHER-reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_ACT},
                                                                                            False)),
                                                     PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsNothing())
        actual = FileRefTestImpl(RelOptionType.REL_RESULT,
                                 PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_RESULT,
                                   PathPartAsNothing())
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    _relativity_restriction({RelOptionType.REL_ACT},
                                                                                            False)),
                                                     PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                      _relativity_restriction({RelOptionType.REL_ACT},
                                                                                              False)),
                                                       PathPartAsNothing())
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name',
                                                                    NoRestriction()),
                                                     PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')


class TestNotEquals_DifferentTypeOfPathSuffix(unittest.TestCase):
    def test_without_symbol_ref_in_root_part__expected_is_symbol_reference(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT,
                                   PathPartAsNothing())
        actual = FileRefTestImpl(RelOptionType.REL_ACT,
                                 PathPartAsFixedPath('name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_without_symbol_ref_in_root_part__expected_is_fixed_path(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT,
                                   PathPartAsFixedPath('name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT,
                                 PathPartAsNothing())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_with_symbol_ref_in_root_part(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name', NoRestriction()),
                                                       PathPartAsNothing())
        actual = FileRefWithValRefInRootPartTestImpl(ValueReference('reffed-name', NoRestriction()),
                                                     PathPartAsFixedPath('name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.file_ref_resolver_equals(FileRefConstant(expected))
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')


class Test2NotEquals(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver2(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver2(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver2(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> FileRefRelativityRestriction:
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
