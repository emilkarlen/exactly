import unittest

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.data.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.sym_ref.data.reference_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.type_val_deps.sym_ref.data.value_restrictions import AnyDataTypeRestriction, \
    PathRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    equals_data_type_symbol_references
from exactly_lib_test.type_val_deps.types.path.test_resources import sdv_assertions as sut
from exactly_lib_test.type_val_deps.types.path.test_resources.path_sdvs import \
    PathSdvTestImplWithConstantPathAndSymbolReferences
from exactly_lib_test.type_val_deps.types.path.test_resources.simple_path import PathDdvTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEqualsCommonToBothAssertionMethods(),
        unittest.makeSuite(Test1NotEquals),
        unittest.makeSuite(Test2NotEquals),
    ])


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HDS_CASE
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT

_PATH_SUFFIX_VARIANTS = [
    path_ddvs.constant_path_part('file-name'),
    path_ddvs.empty_path_part(),
]

_RELATIVITY_VARIANTS = [
    _EXISTS_PRE_SDS_RELATIVITY,
    _NOT_EXISTS_PRE_SDS_RELATIVITY,
]

_SYMBOL_REFERENCES = [
    [],
    [SymbolReference('symbol_name',
                     ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))]
]


class TestEqualsCommonToBothAssertionMethods(unittest.TestCase):
    def runTest(self):
        symbols = empty_symbol_table()
        for relativity in _RELATIVITY_VARIANTS:
            for path_suffix in _PATH_SUFFIX_VARIANTS:
                for symbol_references in _SYMBOL_REFERENCES:
                    path = PathDdvTestImpl(relativity, path_suffix)
                    path_sdv = PathSdvTestImplWithConstantPathAndSymbolReferences(path,
                                                                                  symbol_references)
                    test_case_descr = 'relativity:{}, path-suffix: {}'.format(relativity, type(path_suffix))
                    with self.subTest(msg=sut.equals_path_sdv.__name__ + ' :: ' + test_case_descr):
                        assertion = sut.equals_path_sdv(path_sdv)
                        assertion.apply_without_message(self, path_sdv)
                    with self.subTest(msg=sut.matches_path_sdv.__name__ + ' :: ' + test_case_descr):
                        assertion = sut.matches_path_sdv(path,
                                                         equals_data_type_symbol_references(
                                                             path_sdv.references),
                                                         symbols)
                        assertion.apply_without_message(self, path_sdv)


class TestNotEqualsWithoutSymbolReferencesCommonToBothAssertionMethods(unittest.TestCase):
    def test_difference_in_relativity_root(self):
        symbols = empty_symbol_table()
        for relativity in _RELATIVITY_VARIANTS:
            for path_suffix in _PATH_SUFFIX_VARIANTS:
                test_case_descr = 'relativity:{}, path-suffix: {}'.format(relativity, type(path_suffix))
                path = PathDdvTestImpl(relativity, path_suffix)
                path_sdv = path_sdvs.constant(path)
                with self.subTest(msg=sut.equals_path_sdv.__name__ + ' :: ' + test_case_descr):
                    assertion = sut.equals_path_sdv(path_sdv)
                    assertion.apply_without_message(self, path_sdv)
                with self.subTest(msg=sut.matches_path_sdv.__name__ + ' :: ' + test_case_descr):
                    assertion = sut.matches_path_sdv(path,
                                                     equals_data_type_symbol_references(path_sdv.references),
                                                     symbols)
                    assertion.apply_without_message(self, path_sdv)


class Test1NotEquals(unittest.TestCase):
    def test_differs__paths(self):
        # ARRANGE #
        symbol_references = []
        expected = sdv_from_constants(path_with_fixed_suffix('expected'),
                                      symbol_references)
        actual = sdv_from_constants(path_with_fixed_suffix('not_expected'),
                                    symbol_references)
        assertion = sut.equals_path_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_value_ref__differs__restriction_relativity_variants(self):
        # ARRANGE #
        def restriction_with_relativity(relativity: RelOptionType) -> ValueRestriction:
            return _relativity_restriction({relativity},
                                           False)

        path = arbitrary_path()
        expected = sdv_from_constants(
            path,
            [SymbolReference('reffed-name',
                             ReferenceRestrictionsOnDirectAndIndirect(
                                 restriction_with_relativity(RelOptionType.REL_ACT)))])
        actual = sdv_from_constants(
            path,
            [SymbolReference('reffed-name',
                             ReferenceRestrictionsOnDirectAndIndirect(
                                 restriction_with_relativity(RelOptionType.REL_HDS_CASE)))])
        assertion = sut.equals_path_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_value_ref__differs__symbol_name(self):
        # ARRANGE #
        path = arbitrary_path()
        expected = sdv_from_constants(path,
                                      [SymbolReference('expected_symbol_name',
                                                       ReferenceRestrictionsOnDirectAndIndirect(
                                                           AnyDataTypeRestriction()))])
        actual = sdv_from_constants(path,
                                    [SymbolReference('actual_symbol_name',
                                                     ReferenceRestrictionsOnDirectAndIndirect(
                                                         AnyDataTypeRestriction()))])
        assertion = sut.equals_path_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        path = arbitrary_path()
        expected = sdv_from_constants(path,
                                      [SymbolReference('reffed-name',
                                                       ReferenceRestrictionsOnDirectAndIndirect(
                                                           AnyDataTypeRestriction()))])
        actual = sdv_from_constants(path, [])
        # ACT & ASSERT #
        assertion = sut.equals_path_sdv(expected)
        assert_that_assertion_fails(assertion, actual)

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        path = arbitrary_path()
        expected = sdv_from_constants(path, [])
        actual = sdv_from_constants(path,
                                    [SymbolReference('reffed-name',
                                                     ReferenceRestrictionsOnDirectAndIndirect(
                                                         AnyDataTypeRestriction()))])
        assertion = sut.equals_path_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        path = arbitrary_path()
        expected = sdv_from_constants(path,
                                      [SymbolReference('reffed-name',
                                                       ReferenceRestrictionsOnDirectAndIndirect(
                                                           _relativity_restriction(
                                                               {RelOptionType.REL_ACT},
                                                               False)))])
        actual = sdv_from_constants(path,
                                    [SymbolReference('reffed-name',
                                                     ReferenceRestrictionsOnDirectAndIndirect(
                                                         AnyDataTypeRestriction()))])
        assertion = sut.equals_path_sdv(expected)
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


class Test2NotEquals(unittest.TestCase):
    def test_differs__path_suffix(self):
        # ARRANGE #
        expected = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('other-file-name'))
        assertion = sut.matches_path_sdv(expected, asrt.ignore, empty_symbol_table())
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, path_sdvs.constant(actual))

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        expected = PathDdvTestImpl(_EXISTS_PRE_SDS_RELATIVITY, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, path_ddvs.constant_path_part('file-name'))
        assertion = sut.matches_path_sdv(expected, asrt.ignore, empty_symbol_table())
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, path_sdvs.constant(actual))

    def test_differs__relativity(self):
        # ARRANGE #
        expected = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(RelOptionType.REL_HDS_CASE, path_ddvs.constant_path_part('file-name'))
        assertion = sut.matches_path_sdv(expected, asrt.ignore, empty_symbol_table())
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, path_sdvs.constant(actual))

    def test_differs__symbol_references(self):
        # ARRANGE #
        path = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('file-name'))
        actual = PathSdvTestImplWithConstantPathAndSymbolReferences(
            path,
            [SymbolReference('symbol_name',
                             ReferenceRestrictionsOnDirectAndIndirect(AnyDataTypeRestriction()))])
        assertion = sut.matches_path_sdv(path,
                                         asrt.matches_sequence([]),
                                         empty_symbol_table())
        # ACT & ASSERT #
        assert_that_assertion_fails(assertion, actual)


def arbitrary_path() -> PathDdv:
    return PathDdvTestImpl(RelOptionType.REL_TMP, path_ddvs.constant_path_part('path-suffix'))


def path_with_fixed_suffix(suffix_name: str) -> PathDdv:
    return PathDdvTestImpl(RelOptionType.REL_TMP, path_ddvs.constant_path_part(suffix_name))


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> PathRelativityRestriction:
    return PathRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))


def sdv_from_constants(path: PathDdv, references: list) -> PathSdv:
    return PathSdvTestImplWithConstantPathAndSymbolReferences(path, references)
