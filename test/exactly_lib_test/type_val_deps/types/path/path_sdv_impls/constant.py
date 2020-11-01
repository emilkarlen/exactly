import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_sdv_impls import constant as sut
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.tcfs.test_resources.simple_path import PathDdvTestImpl
from exactly_lib_test.type_val_deps.types.path.test_resources.path_assertions import equals_path


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestPathConstant)


class TestPathConstant(unittest.TestCase):
    def test_resolved_value(self):
        # ARRANGE #
        path = PathDdvTestImpl(RelOptionType.REL_TMP, path_ddvs.empty_path_part())
        sdv = sut.PathConstantSdv(path)
        # ACT #
        actual = sdv.resolve(empty_symbol_table())
        # ASSERT #
        assertion = equals_path(path)
        assertion.apply_without_message(self, actual)
