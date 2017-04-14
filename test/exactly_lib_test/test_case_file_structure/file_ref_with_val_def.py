import pathlib
import unittest

from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure import sandbox_directory_structure as _sds
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.util.symbol_table import singleton_symbol_table, Entry
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.value_resolvers import file_ref_with_val_def as sut
from exactly_lib.value_definition.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath, \
    PathPartResolverAsStringSymbolReference
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import concrete_restriction_assertion as restrictions
from exactly_lib_test.value_definition.test_resources import value_definition_utils as sym_utils
from exactly_lib_test.value_definition.test_resources import value_reference_assertions as vr_tr
from exactly_lib_test.value_definition.test_resources.value_definition_utils import string_value_container


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelValueDefinition))
    return ret_val


class TestRelValueDefinition(unittest.TestCase):
    def test_value_references(self):
        # ARRANGE #
        expected_restriction = FileRefRelativityRestriction(
            PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, True))
        expected_mandatory_references = [
            vr_tr.equals_value_reference('value_definition_name',
                                         restrictions.equals_file_ref_relativity_restriction(expected_restriction))
        ]
        value_ref_of_path = ValueReference('value_definition_name', expected_restriction)
        path_suffix_test_cases = [
            (PathPartResolverAsFixedPath('file.txt'),
             [],
             ),
            (PathPartResolverAsStringSymbolReference('symbol_name'),
             [vr_tr.equals_value_reference('symbol_name', restrictions.is_string_value_restriction)],
             ),
        ]
        for path_suffix, additional_expected_references in path_suffix_test_cases:
            file_ref_resolver = sut.rel_value_definition(value_ref_of_path, path_suffix)
            # ACT #
            actual = file_ref_resolver.references
            # ASSERT #
            expected_references = expected_mandatory_references + additional_expected_references
            assertion = asrt.matches_sequence(expected_references)
            assertion.apply_with_message(self, actual, 'value_references_of_paths')

    def test_exists_pre_sds(self):
        # ARRANGE #
        relativity_test_cases = [
            (RelOptionType.REL_HOME,
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
            (PathPartResolverAsStringSymbolReference('path_suffix_symbol_name'),
             (Entry('path_suffix_symbol_name',
                    string_value_container('path-suffix')),),
             ),
        ]
        file_ref_symbol_name = 'VAL_DEF_NAME'
        for rel_option_type_of_referenced_symbol, expected_exists_pre_sds in relativity_test_cases:
            referenced_file_ref = file_refs.of_rel_option(rel_option_type_of_referenced_symbol,
                                                          PathPartAsFixedPath('referenced-file-name'))
            for path_suffix, sym_tbl_entries in path_suffix_test_cases:
                symbol_table = singleton_symbol_table(
                    sym_utils.entry(file_ref_symbol_name,
                                    sym_utils.file_ref_value(file_ref=referenced_file_ref)))
                symbol_table.add_all(sym_tbl_entries)
                with self.subTest(msg='rel_option_type={} ,path_suffix_type={}'.format(
                        rel_option_type_of_referenced_symbol,
                        path_suffix)):
                    file_ref_resolver_to_check = sut.rel_value_definition(
                        _value_reference_of_path_with_accepted(file_ref_symbol_name,
                                                               rel_option_type_of_referenced_symbol),
                        path_suffix)
                    # ACT #
                    actual = file_ref_resolver_to_check.resolve(symbol_table).exists_pre_sds(symbol_table)
                    # ASSERT #
                    self.assertEqual(expected_exists_pre_sds,
                                     actual,
                                     'existence pre SDS')

    def test_file_path(self):
        relativity_test_cases = [
            (RelOptionType.REL_HOME, True),
            (RelOptionType.REL_ACT, False),
        ]
        path_suffix_str = 'path-suffix-file.txt'
        path_suffix_test_cases = [
            (PathPartResolverAsFixedPath(path_suffix_str), ()
             ),
            (PathPartResolverAsStringSymbolReference('path_suffix_symbol'),
             (Entry('path_suffix_symbol',
                    string_value_container(path_suffix_str)),)
             ),
        ]
        for rel_option, exists_pre_sds in relativity_test_cases:
            # ARRANGE #
            file_ref_symbol_name = 'file_ref_symbol'
            path_component_from_referenced_file_ref = 'path-component-from-referenced-file-ref'
            referenced_entry = sym_utils.entry(
                file_ref_symbol_name,
                sym_utils.file_ref_value(
                    file_ref=file_refs.of_rel_option(rel_option,
                                                     PathPartAsFixedPath(
                                                         path_component_from_referenced_file_ref))))
            for path_suffix, symbol_table_entries in path_suffix_test_cases:
                fr_resolver_to_check = sut.rel_value_definition(
                    _value_reference_of_path_with_accepted(file_ref_symbol_name,
                                                           rel_option),
                    path_suffix)
                symbol_table = singleton_symbol_table(referenced_entry)
                symbol_table.add_all(symbol_table_entries)
                home_and_sds = _home_and_sds()
                expected_root_path = _root_path_of_option(rel_option, home_and_sds)
                expected_path = expected_root_path / path_component_from_referenced_file_ref / path_suffix_str
                expected_path_str = str(expected_path)
                environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, symbol_table)
                with self.subTest(msg=str(rel_option)):
                    # ACT #
                    file_ref_to_check = fr_resolver_to_check.resolve(symbol_table)
                    if exists_pre_sds:
                        tested_path_msg = 'file_path_pre_sds'
                        actual_path = file_ref_to_check.file_path_pre_sds(environment)
                    else:
                        tested_path_msg = 'file_path_post_sds'
                        actual_path = file_ref_to_check.file_path_post_sds(environment)
                    actual_path_pre_or_post_sds = file_ref_to_check.file_path_pre_or_post_sds(environment)
                    # ASSERT #
                    self.assertEqual(expected_path_str,
                                     str(actual_path),
                                     tested_path_msg)
                    self.assertEqual(expected_path_str,
                                     str(actual_path_pre_or_post_sds),
                                     'file_path_pre_or_post_sds')


def _value_reference_of_path_with_accepted(value_name: str,
                                           accepted: RelOptionType) -> ValueReference:
    return ValueReference(value_name,
                          FileRefRelativityRestriction(_path_relativity_variants_with(accepted)))


def _path_relativity_variants_with(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


def _home_and_sds() -> HomeAndSds:
    return HomeAndSds(pathlib.Path('home'),
                      _sds.SandboxDirectoryStructure('sds'))


def _root_path_of_option(rel_option: RelOptionType, home_and_sds: HomeAndSds) -> pathlib.Path:
    resolver = REL_OPTIONS_MAP[rel_option].root_resolver
    return resolver.from_home_and_sds(home_and_sds)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
