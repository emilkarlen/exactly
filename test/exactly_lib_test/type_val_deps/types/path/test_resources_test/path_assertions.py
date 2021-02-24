import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.type_val_deps.types.path.test_resources import path_assertions as sut
from exactly_lib_test.type_val_deps.types.path.test_resources.simple_path import \
    PathDdvTestImpl


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEquals(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Exists pre SDS/fixed path suffix',
             PathDdvTestImpl(_EXISTS_PRE_SDS_RELATIVITY,
                             path_ddvs.constant_path_part('file-name')),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             PathDdvTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                             path_ddvs.constant_path_part('a-file-name')),
             ),
        ]
        for test_case_name, ddv in test_cases:
            assert isinstance(ddv, PathDdv), 'Type info for IDE'
            with self.subTest(test_case_name):
                assertion = sut.equals_path(ddv)
                assertion.apply_without_message(self, ddv)


class TestNotEquals_PathSuffixAsFixedPath(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_path(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathDdvTestImpl(_EXISTS_PRE_SDS_RELATIVITY, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(_NOT_EXISTS_PRE_SDS_RELATIVITY, path_ddvs.constant_path_part('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_path(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathDdvTestImpl(RelOptionType.REL_ACT, path_ddvs.constant_path_part('file-name'))
        actual = PathDdvTestImpl(RelOptionType.REL_HDS_CASE, path_ddvs.constant_path_part('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_path(expected).apply_with_message(put, actual, 'NotEquals')


class TestNotEquals_DifferentTypeOfPathSuffix(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = PathDdvTestImpl(RelOptionType.REL_ACT,
                                   path_ddvs.constant_path_part('name'))
        actual = PathDdvTestImpl(RelOptionType.REL_ACT,
                                 path_ddvs.empty_path_part())
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.equals_path(expected).apply_with_message(put, actual, 'NotEquals')


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HDS_CASE
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> PathAndRelativityRestriction:
    return PathAndRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
