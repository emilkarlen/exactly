import unittest

from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.symbol.restriction import ValueRestriction
from exactly_lib.symbol.restrictions.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.restrictions.value_restrictions import NoRestriction, FileRefRelativityRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing
from exactly_lib.type_system_values.file_ref import FileRef
from exactly_lib.util.symbol_table import empty_symbol_table, SymbolTable
from exactly_lib_test.symbol.test_resources import concrete_value_assertions as sut
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import FileRefTestImpl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEqualsCommonToBothAssertionMethods(),
        unittest.makeSuite(Test1NotEquals),
        unittest.makeSuite(Test2NotEquals),
    ])


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT

_PATH_SUFFIX_VARIANTS = [
    PathPartAsFixedPath('file-name'),
    PathPartAsNothing(),
]

_RELATIVITY_VARIANTS = [
    _EXISTS_PRE_SDS_RELATIVITY,
    _NOT_EXISTS_PRE_SDS_RELATIVITY,
]

_SYMBOL_REFERENCES = [
    [],
    [SymbolReference('symbol_name',
                     ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))]
]


class TestEqualsCommonToBothAssertionMethods(unittest.TestCase):
    def runTest(self):
        symbols = empty_symbol_table()
        for relativity in _RELATIVITY_VARIANTS:
            for path_suffix in _PATH_SUFFIX_VARIANTS:
                for symbol_references in _SYMBOL_REFERENCES:
                    file_ref = FileRefTestImpl(relativity, path_suffix)
                    file_ref_resolver = _FileRefResolverWithConstantFileRefAndSymbolReferences(file_ref,
                                                                                               symbol_references)
                    test_case_descr = 'relativity:{}, path-suffix: {}'.format(relativity, type(path_suffix))
                    with self.subTest(msg=sut.equals_file_ref_resolver.__name__ + ' :: ' + test_case_descr):
                        assertion = sut.equals_file_ref_resolver(file_ref_resolver)
                        assertion.apply_without_message(self, file_ref_resolver)
                    with self.subTest(msg=sut.matches_file_ref_resolver.__name__ + ' :: ' + test_case_descr):
                        assertion = sut.matches_file_ref_resolver(file_ref,
                                                                  equals_symbol_references(
                                                                      file_ref_resolver.references),
                                                                  symbols)
                        assertion.apply_without_message(self, file_ref_resolver)


class TestNotEqualsWithoutSymbolReferencesCommonToBothAssertionMethods(unittest.TestCase):
    def test_difference_in_relativity_root(self):
        symbols = empty_symbol_table()
        for relativity in _RELATIVITY_VARIANTS:
            for path_suffix in _PATH_SUFFIX_VARIANTS:
                test_case_descr = 'relativity:{}, path-suffix: {}'.format(relativity, type(path_suffix))
                file_ref = FileRefTestImpl(relativity, path_suffix)
                file_ref_resolver = FileRefConstant(file_ref)
                with self.subTest(msg=sut.equals_file_ref_resolver.__name__ + ' :: ' + test_case_descr):
                    assertion = sut.equals_file_ref_resolver(file_ref_resolver)
                    assertion.apply_without_message(self, file_ref_resolver)
                with self.subTest(msg=sut.matches_file_ref_resolver.__name__ + ' :: ' + test_case_descr):
                    assertion = sut.matches_file_ref_resolver(file_ref,
                                                              equals_symbol_references(file_ref_resolver.references),
                                                              symbols)
                    assertion.apply_without_message(self, file_ref_resolver)


class Test1NotEquals(unittest.TestCase):
    def test_differs__file_refs(self):
        # ARRANGE #
        symbol_references = []
        expected = resolver_from_constants(file_ref_with_fixed_suffix('expected'),
                                           symbol_references)
        actual = resolver_from_constants(file_ref_with_fixed_suffix('not_expected'),
                                         symbol_references)
        assertion = sut.equals_file_ref_resolver(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


    def test_value_ref__differs__restriction_relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()

        def restriction_with_relativity(relativity: RelOptionType) -> ValueRestriction:
            return _relativity_restriction({relativity},
                                           False)

        file_ref = arbitrary_file_ref()
        expected = resolver_from_constants(
            file_ref,
            [SymbolReference('reffed-name',
                             ReferenceRestrictionsOnDirectAndIndirect(
                                 restriction_with_relativity(RelOptionType.REL_ACT)))])
        actual = resolver_from_constants(
            file_ref,
            [SymbolReference('reffed-name',
                             ReferenceRestrictionsOnDirectAndIndirect(
                                 restriction_with_relativity(RelOptionType.REL_HOME)))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_value_ref__differs__symbol_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref = arbitrary_file_ref()
        expected = resolver_from_constants(file_ref,
                                           [SymbolReference('expected_symbol_name',
                                                            ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        actual = resolver_from_constants(file_ref,
                                         [SymbolReference('actual_symbol_name',
                                                          ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref = arbitrary_file_ref()
        expected = resolver_from_constants(file_ref,
                                           [SymbolReference('reffed-name',
                                                            ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        actual = resolver_from_constants(file_ref, [])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref = arbitrary_file_ref()
        expected = resolver_from_constants(file_ref, [])
        actual = resolver_from_constants(file_ref,
                                         [SymbolReference('reffed-name',
                                                          ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver(expected)
            assertion.apply_without_message(put, actual)

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref = arbitrary_file_ref()
        expected = resolver_from_constants(file_ref,
                                           [SymbolReference('reffed-name',
                                                            ReferenceRestrictionsOnDirectAndIndirect(
                                                                _relativity_restriction(
                                                                    {RelOptionType.REL_ACT},
                                                                    False)))])
        actual = resolver_from_constants(file_ref,
                                         [SymbolReference('reffed-name',
                                                          ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref_resolver(expected)
            assertion.apply_without_message(put, actual)


class Test2NotEquals(unittest.TestCase):
    def test_differs__path_suffix(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.matches_file_ref_resolver(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.matches_file_ref_resolver(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = FileRefTestImpl(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.matches_file_ref_resolver(expected, asrt.ignore, empty_symbol_table())
            assertion.apply_with_message(put, FileRefConstant(actual), 'NotEquals')

    def test_differs__symbol_references(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        file_ref = FileRefTestImpl(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = _FileRefResolverWithConstantFileRefAndSymbolReferences(
            file_ref,
            [SymbolReference('symbol_name', ReferenceRestrictionsOnDirectAndIndirect(NoRestriction()))])
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.matches_file_ref_resolver(file_ref,
                                                      asrt.matches_sequence([]),
                                                      empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')


def arbitrary_file_ref() -> FileRef:
    return FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsFixedPath('path-suffix'))


def file_ref_with_fixed_suffix(suffix_name: str) -> FileRef:
    return FileRefTestImpl(RelOptionType.REL_TMP, PathPartAsFixedPath(suffix_name))


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> FileRefRelativityRestriction:
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))


def resolver_from_constants(file_ref: FileRef, references: list) -> FileRefResolver:
    return _FileRefResolverWithConstantFileRefAndSymbolReferences(file_ref, references)


class _FileRefResolverWithConstantFileRefAndSymbolReferences(FileRefResolver):
    def __init__(self,
                 file_ref: FileRef,
                 references: list):
        self._file_ref = file_ref
        self._references = references

    @property
    def references(self) -> list:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FileRef:
        return self._file_ref
