import pathlib
import unittest

from exactly_lib.symbol.data import path_part_sdvs
from exactly_lib.symbol.data.path_sdv_impls import path_with_symbol as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    is_any_data_type
from exactly_lib.symbol.data.restrictions.value_restrictions import AnyDataTypeRestriction, \
    PathRelativityRestriction
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.symbol.data.restrictions.test_resources import \
    concrete_restriction_assertion as restrictions
from exactly_lib_test.symbol.data.test_resources import symbol_reference_assertions as vr_tr
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.data.test_resources.sdvs import \
    string_sdv_of_single_symbol_reference
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestRelSymbol)


class TestRelSymbol(unittest.TestCase):
    def test_symbol_references(self):
        # ARRANGE #
        expected_restriction = PathRelativityRestriction(
            PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HDS_CASE}, True))
        symbol_name_of_rel_path = 'symbol_name_of_rel_path'
        symbol_name_of_path_suffix = 'symbol_name_of_path_suffix'
        restrictions_on_path_suffix_symbol = restrictions.ReferenceRestrictionsOnDirectAndIndirect(
            AnyDataTypeRestriction()
        )
        expected_mandatory_references = [
            vr_tr.equals_symbol_reference_with_restriction_on_direct_target(
                symbol_name_of_rel_path,
                restrictions.equals_path_relativity_restriction(expected_restriction))
        ]
        symbol_ref_of_path = SymbolReference(symbol_name_of_rel_path,
                                             ReferenceRestrictionsOnDirectAndIndirect(expected_restriction))
        path_suffix_test_cases = [
            (path_part_sdvs.from_constant_str('file.txt'),
             [],
             ),
            (path_part_sdvs.from_string(
                string_sdv_of_single_symbol_reference(symbol_name_of_path_suffix,
                                                      restrictions_on_path_suffix_symbol)),
             [asrt_sym_usage.matches_reference_2(
                 symbol_name_of_path_suffix,
                 vr_tr.matches_restrictions_on_direct_and_indirect())],
            ),
        ]
        for path_suffix_sdv, additional_expected_references in path_suffix_test_cases:
            path_sdv = sut.PathSdvRelSymbol(path_suffix_sdv, symbol_ref_of_path)
            # ACT #
            actual = path_sdv.references
            # ASSERT #
            expected_references = expected_mandatory_references + additional_expected_references
            assertion = asrt.matches_sequence(expected_references)
            assertion.apply_with_message(self, actual, 'symbol references')

    def test_exists_pre_sds(self):
        # ARRANGE #
        relativity_test_cases = [
            (RelOptionType.REL_HDS_CASE,
             True,
             ),
            (RelOptionType.REL_TMP,
             False,
             ),
        ]
        path_suffix_test_cases = [
            (path_part_sdvs.from_constant_str('file.txt'),
             []
             ),
            (path_part_sdvs.from_string(string_sdv_of_single_symbol_reference('path_suffix_symbol_name',
                                                                              is_any_data_type())),
             [StringConstantSymbolContext('path_suffix_symbol_name', 'path-suffix').entry],
             ),
        ]
        for rel_option_type_of_referenced_symbol, expected_exists_pre_sds in relativity_test_cases:
            referenced_path = ConstantSuffixPathDdvSymbolContext('SYMBOL_NAME',
                                                                 rel_option_type_of_referenced_symbol,
                                                                 'referenced-file-name')
            for path_suffix, sym_tbl_entries in path_suffix_test_cases:
                symbol_table = referenced_path.symbol_table
                symbol_table.add_all(sym_tbl_entries)
                with self.subTest(msg='rel_option_type={} ,path_suffix_type={}'.format(
                        rel_option_type_of_referenced_symbol,
                        path_suffix)):
                    path_sdv_to_check = sut.PathSdvRelSymbol(
                        path_suffix,
                        _symbol_reference_of_path_with_accepted(referenced_path.name,
                                                                rel_option_type_of_referenced_symbol))
                    # ACT #
                    actual = path_sdv_to_check.resolve(symbol_table).exists_pre_sds()
                    # ASSERT #
                    self.assertEqual(expected_exists_pre_sds,
                                     actual,
                                     'existence pre SDS')

    def test_file_path(self):
        relativity_test_cases = [
            (RelOptionType.REL_HDS_CASE, True),
            (RelOptionType.REL_ACT, False),
        ]
        path_suffix_str = 'path-suffix-file.txt'
        path_suffix_test_cases = [
            (path_part_sdvs.from_constant_str(path_suffix_str),
             ()
             ),
            (path_part_sdvs.from_string(string_sdv_of_single_symbol_reference('path_suffix_symbol',
                                                                              is_any_data_type())),
             (StringConstantSymbolContext('path_suffix_symbol',
                                          path_suffix_str).entry,)
             ),
        ]
        for rel_option, exists_pre_sds in relativity_test_cases:
            # ARRANGE #
            path_component_from_referenced_path = 'path-component-from-referenced-file-ref'
            referenced_sym = ConstantSuffixPathDdvSymbolContext('path_symbol',
                                                                rel_option,
                                                                path_component_from_referenced_path)

            for path_suffix, symbol_table_entries in path_suffix_test_cases:
                fr_sdv_to_check = sut.PathSdvRelSymbol(
                    path_suffix,
                    _symbol_reference_of_path_with_accepted(referenced_sym.name,
                                                            rel_option))
                symbol_table = referenced_sym.symbol_table
                symbol_table.add_all(symbol_table_entries)
                tcds = fake_tcds()
                expected_root_path = _root_path_of_option(rel_option, tcds)
                expected_path = expected_root_path / path_component_from_referenced_path / path_suffix_str
                expected_path_str = str(expected_path)
                environment = PathResolvingEnvironmentPreOrPostSds(tcds, symbol_table)
                with self.subTest(msg=str(rel_option)):
                    # ACT #
                    path_to_check = fr_sdv_to_check.resolve(environment.symbols)
                    if exists_pre_sds:
                        tested_path_msg = 'value_pre_sds'
                        actual_path = path_to_check.value_pre_sds(environment.hds)
                    else:
                        tested_path_msg = 'value_post_sds'
                        actual_path = path_to_check.value_post_sds(environment.sds)
                    actual_path_pre_or_post_sds = path_to_check.value_of_any_dependency(environment.tcds)
                    # ASSERT #
                    self.assertEqual(expected_path_str,
                                     str(actual_path),
                                     tested_path_msg)
                    self.assertEqual(expected_path_str,
                                     str(actual_path_pre_or_post_sds),
                                     'value_of_any_dependency')


def _symbol_reference_of_path_with_accepted(value_name: str,
                                            accepted: RelOptionType) -> SymbolReference:
    return SymbolReference(value_name,
                           ReferenceRestrictionsOnDirectAndIndirect(
                               PathRelativityRestriction(_path_relativity_variants_with(accepted))))


def _path_relativity_variants_with(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


def _root_path_of_option(rel_option: RelOptionType, tcds: Tcds) -> pathlib.Path:
    resolver = REL_OPTIONS_MAP[rel_option].root_resolver
    return resolver.from_tcds(tcds)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
