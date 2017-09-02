import pathlib
import unittest

from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    no_restrictions
from exactly_lib.named_element.symbol.restrictions.value_restrictions import AnySymbolTypeRestriction, \
    FileRefRelativityRestriction
from exactly_lib.named_element.symbol.value_resolvers import file_ref_with_symbol as sut
from exactly_lib.named_element.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath, \
    PathPartResolverAsStringResolver
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.value_type import SymbolValueType, ValueType
from exactly_lib.util.symbol_table import Entry, singleton_symbol_table_2
from exactly_lib_test.named_element.symbol.restrictions.test_resources import \
    concrete_restriction_assertion as restrictions
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils as sym_utils, \
    symbol_reference_assertions as vr_tr
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import string_constant_container
from exactly_lib_test.named_element.symbol.test_resources.value_resolvers import \
    string_resolver_of_single_symbol_reference
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelSymbol))
    return ret_val


class TestRelSymbol(unittest.TestCase):
    def test_symbol_references(self):
        # ARRANGE #
        expected_restriction = FileRefRelativityRestriction(
            PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME_CASE}, True))
        symbol_name_of_rel_path = 'symbol_name_of_rel_path'
        symbol_name_of_path_suffix = 'symbol_name_of_path_suffix'
        restrictions_on_path_suffix_symbol = restrictions.ReferenceRestrictionsOnDirectAndIndirect(
            AnySymbolTypeRestriction())
        expected_mandatory_references = [
            vr_tr.equals_symbol_reference_with_restriction_on_direct_target(
                symbol_name_of_rel_path,
                restrictions.equals_file_ref_relativity_restriction(expected_restriction))
        ]
        symbol_ref_of_path = NamedElementReference(symbol_name_of_rel_path,
                                                   ReferenceRestrictionsOnDirectAndIndirect(expected_restriction))
        path_suffix_test_cases = [
            (PathPartResolverAsFixedPath('file.txt'),
             [],
             ),
            (PathPartResolverAsStringResolver(
                string_resolver_of_single_symbol_reference(symbol_name_of_path_suffix,
                                                           restrictions_on_path_suffix_symbol)),
             [resolver_structure_assertions.matches_reference_2(
                 symbol_name_of_path_suffix,
                 vr_tr.matches_restrictions_on_direct_and_indirect())],
            ),
        ]
        for path_suffix_resolver, additional_expected_references in path_suffix_test_cases:
            file_ref_resolver = sut.rel_symbol(symbol_ref_of_path, path_suffix_resolver)
            # ACT #
            actual = file_ref_resolver.references
            # ASSERT #
            expected_references = expected_mandatory_references + additional_expected_references
            assertion = asrt.matches_sequence(expected_references)
            assertion.apply_with_message(self, actual, 'symbol references')

    def test_exists_pre_sds(self):
        # ARRANGE #
        relativity_test_cases = [
            (RelOptionType.REL_HOME_CASE,
             True,
             ),
            (RelOptionType.REL_TMP,
             False,
             ),
        ]
        path_suffix_test_cases = [
            (PathPartResolverAsFixedPath('file.txt'),
             ()
             ),
            (PathPartResolverAsStringResolver(string_resolver_of_single_symbol_reference('path_suffix_symbol_name',
                                                                                         no_restrictions())),
             (Entry('path_suffix_symbol_name',
                    string_constant_container('path-suffix')),),
             ),
        ]
        file_ref_symbol_name = 'SYMBOL_NAME'
        for rel_option_type_of_referenced_symbol, expected_exists_pre_sds in relativity_test_cases:
            referenced_file_ref = file_refs.of_rel_option(rel_option_type_of_referenced_symbol,
                                                          PathPartAsFixedPath('referenced-file-name'))
            for path_suffix, sym_tbl_entries in path_suffix_test_cases:
                symbol_table = singleton_symbol_table_2(
                    file_ref_symbol_name,
                    sym_utils.file_ref_constant_container(referenced_file_ref))
                symbol_table.add_all(sym_tbl_entries)
                with self.subTest(msg='rel_option_type={} ,path_suffix_type={}'.format(
                        rel_option_type_of_referenced_symbol,
                        path_suffix)):
                    file_ref_resolver_to_check = sut.rel_symbol(
                        _symbol_reference_of_path_with_accepted(file_ref_symbol_name,
                                                                rel_option_type_of_referenced_symbol),
                        path_suffix)
                    # ACT #
                    actual = file_ref_resolver_to_check.resolve(symbol_table).exists_pre_sds()
                    # ASSERT #
                    self.assertEqual(expected_exists_pre_sds,
                                     actual,
                                     'existence pre SDS')

    def test_file_path_and_value_type(self):
        relativity_test_cases = [
            (RelOptionType.REL_HOME_CASE, True),
            (RelOptionType.REL_ACT, False),
        ]
        path_suffix_str = 'path-suffix-file.txt'
        path_suffix_test_cases = [
            (PathPartResolverAsFixedPath(path_suffix_str), ()
             ),
            (PathPartResolverAsStringResolver(string_resolver_of_single_symbol_reference('path_suffix_symbol',
                                                                                         no_restrictions())),
             (Entry('path_suffix_symbol',
                    string_constant_container(path_suffix_str)),)
             ),
        ]
        for rel_option, exists_pre_sds in relativity_test_cases:
            # ARRANGE #
            path_component_from_referenced_file_ref = 'path-component-from-referenced-file-ref'
            referenced_sym = NameAndValue('file_ref_symbol',
                                          sym_utils.file_ref_constant_container(
                                              file_refs.of_rel_option(rel_option,
                                                                      PathPartAsFixedPath(
                                                                          path_component_from_referenced_file_ref))
                                          ))
            for path_suffix, symbol_table_entries in path_suffix_test_cases:
                fr_resolver_to_check = sut.rel_symbol(
                    _symbol_reference_of_path_with_accepted(referenced_sym.name,
                                                            rel_option),
                    path_suffix)
                symbol_table = singleton_symbol_table_2(referenced_sym.name,
                                                        referenced_sym.value)
                symbol_table.add_all(symbol_table_entries)
                home_and_sds = fake_home_and_sds()
                expected_root_path = _root_path_of_option(rel_option, home_and_sds)
                expected_path = expected_root_path / path_component_from_referenced_file_ref / path_suffix_str
                expected_path_str = str(expected_path)
                environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, symbol_table)
                with self.subTest(msg=str(rel_option)):
                    # ACT #
                    file_ref_to_check = fr_resolver_to_check.resolve(environment.symbols)
                    if exists_pre_sds:
                        tested_path_msg = 'value_pre_sds'
                        actual_path = file_ref_to_check.value_pre_sds(environment.hds)
                    else:
                        tested_path_msg = 'value_post_sds'
                        actual_path = file_ref_to_check.value_post_sds(environment.sds)
                    actual_path_pre_or_post_sds = file_ref_to_check.value_of_any_dependency(environment.home_and_sds)
                    # ASSERT #
                    self.assertIs(SymbolValueType.PATH,
                                  fr_resolver_to_check.data_value_type,
                                  'data value type of resolver')
                    self.assertIs(ValueType.PATH,
                                  fr_resolver_to_check.value_type,
                                  'value type of resolver')
                    self.assertEqual(expected_path_str,
                                     str(actual_path),
                                     tested_path_msg)
                    self.assertEqual(expected_path_str,
                                     str(actual_path_pre_or_post_sds),
                                     'value_of_any_dependency')


def _symbol_reference_of_path_with_accepted(value_name: str,
                                            accepted: RelOptionType) -> NamedElementReference:
    return NamedElementReference(value_name,
                                 ReferenceRestrictionsOnDirectAndIndirect(
                                     FileRefRelativityRestriction(_path_relativity_variants_with(accepted))))


def _path_relativity_variants_with(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


def _root_path_of_option(rel_option: RelOptionType, home_and_sds: HomeAndSds) -> pathlib.Path:
    resolver = REL_OPTIONS_MAP[rel_option].root_resolver
    return resolver.from_home_and_sds(home_and_sds)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
