import unittest
from pathlib import Path
from typing import Optional, Sequence

from exactly_lib.impls.types.path import parse_path as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream import TokenStream
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference, SymbolDependentValue
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionArgumentConfiguration, \
    RelOptionsConfiguration
from exactly_lib.util.cli_syntax.elements import argument
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.parse.test_resources import \
    single_line_source_instruction_utils as equivalent_source_variants
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.path.test_resources.sdv_assertions import equals_path_sdv, matches_path_sdv
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathSymbolValueContext


class Arrangement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfiguration,
                 source_file_path: Optional[Path] = None):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration
        self.source_file_path = source_file_path


class Arrangement2:
    def __init__(self,
                 rel_option_argument_configuration: RelOptionArgumentConfiguration,
                 source_file_path: Optional[Path] = None,
                 ):
        self.rel_option_argument_configuration = rel_option_argument_configuration
        self.source_file_path = source_file_path


class Expectation:
    def __init__(self,
                 path_sdv: PathSdv,
                 token_stream: Assertion[TokenStream]):
        assert isinstance(path_sdv, PathSdv)
        self.path_sdv = path_sdv
        self.token_stream = token_stream


class Expectation2:
    def __init__(self,
                 path_sdv: Assertion[SymbolDependentValue],
                 token_stream: Assertion[TokenStream],
                 symbol_table_in_with_all_ref_restrictions_are_satisfied: SymbolTable = None):
        self.path_sdv = path_sdv
        self.token_stream = token_stream
        self.symbol_table_in_with_all_ref_restrictions_are_satisfied = symbol_table_in_with_all_ref_restrictions_are_satisfied


class RelOptionArgumentConfigurationWoSuffixRequirement(tuple):
    def __new__(cls,
                options_configuration: RelOptionsConfiguration,
                argument_syntax_name: str):
        return tuple.__new__(cls, (options_configuration,
                                   argument_syntax_name))

    @property
    def options(self) -> RelOptionsConfiguration:
        return self[0]

    @property
    def argument_syntax_name(self) -> str:
        return self[1]

    def config_for(self, path_suffix_is_required: bool) -> RelOptionArgumentConfiguration:
        return RelOptionArgumentConfiguration(self.options,
                                              self.argument_syntax_name,
                                              path_suffix_is_required)


class ArrangementWoSuffixRequirement:
    def __init__(self,
                 source: str,
                 rel_option_argument_configuration: RelOptionArgumentConfigurationWoSuffixRequirement,
                 source_file_path: Optional[Path] = None):
        self.source = source
        self.rel_option_argument_configuration = rel_option_argument_configuration
        self.source_file_path = source_file_path

    def for_path_suffix_required(self, value: bool) -> Arrangement:
        return Arrangement(self.source,
                           self.rel_option_argument_configuration.config_for(value),
                           self.source_file_path)


ARBITRARY_REL_OPT_ARG_CONF = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants({RelOptionType.REL_ACT}, True),
        RelOptionType.REL_ACT),
    'argument_syntax_name')

ARG_CONFIG_FOR_ALL_RELATIVITIES = RelOptionArgumentConfigurationWoSuffixRequirement(
    RelOptionsConfiguration(
        PathRelativityVariants(RelOptionType, True),
        RelOptionType.REL_HDS_CASE),
    'argument_syntax_name')


def arg_config_with_all_accepted_and_default(default: RelOptionType
                                             ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(PathRelativityVariants(RelOptionType, True),
                                default),
        'argument_syntax_name')


def arg_config_for_rel_symbol_config(relativity_variants: PathRelativityVariants,
                                     default: RelOptionType = None
                                     ) -> RelOptionArgumentConfigurationWoSuffixRequirement:
    if default is None:
        default = list(relativity_variants.rel_option_types)[0]
    return RelOptionArgumentConfigurationWoSuffixRequirement(
        RelOptionsConfiguration(relativity_variants,
                                default),
        'argument_syntax_name')


def option_string_for(option_name: argument.OptionName) -> str:
    return long_option_syntax(option_name.long)


def option_string_for_relativity(relativity: RelOptionType) -> str:
    return option_string_for(REL_OPTIONS_MAP[relativity]._option_name)


def expect(resolved_path: PathDdv,
           expected_symbol_references: Assertion,
           symbol_table: SymbolTable,
           token_stream: Assertion,
           ) -> Expectation2:
    return Expectation2(
        path_sdv=matches_path_sdv(resolved_path,
                                  expected_symbol_references,
                                  symbol_table),
        symbol_table_in_with_all_ref_restrictions_are_satisfied=symbol_table,
        token_stream=token_stream,
    )


class Checker:
    def check(self,
              put: unittest.TestCase,
              arrangement: Arrangement,
              expectation: Expectation):
        # ARRANGE #
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_path(ts,
                                arrangement.rel_option_argument_configuration,
                                arrangement.source_file_path)
        # ASSERT #
        equals_path_sdv(expectation.path_sdv).apply_with_message(put, actual,
                                                                 'path sdv')
        expectation.token_stream.apply_with_message(put, ts, 'token-stream')

    def check__abs_stx__source_variants(self,
                                        put: unittest.TestCase,
                                        source: AbstractSyntax,
                                        arrangement: Arrangement2,
                                        expected_parsed_path: Assertion[PathSdv],
                                        ):
        # ARRANGE #
        parser = sut.PathParser(arrangement.rel_option_argument_configuration)
        for source_variant_case in equivalent_source_variants.expr_parse__s__nsc(source.as_str__default()):
            with put.subTest(source=source_variant_case.name):
                source = source_variant_case.source
                # ACT #
                actual = parser.parse(source, arrangement.source_file_path)
                # ASSERT #
                source_variant_case.expectation.apply_with_message(put, source, 'source')
                expected_parsed_path.apply_with_message(put, actual,
                                                        'path sdv')

    def check2(self,
               put: unittest.TestCase,
               arrangement: Arrangement,
               expectation: Expectation2):
        # ARRANGE #
        ts = TokenStream(arrangement.source)
        # ACT #
        actual = sut.parse_path(ts,
                                arrangement.rel_option_argument_configuration,
                                arrangement.source_file_path)
        # ASSERT #
        self.__assertions_on_reference_restrictions(put, actual,
                                                    expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)
        expectation.path_sdv.apply_with_message(put, actual, 'path-sdv')
        expectation.token_stream.apply_with_message(put, ts, 'token-stream')
        self.__assertions_on_hypothetical_reference_to_sdv(
            put,
            actual,
            expectation.symbol_table_in_with_all_ref_restrictions_are_satisfied)

    def assert_raises_invalid_argument_exception(self,
                                                 put: unittest.TestCase,
                                                 source_string: str,
                                                 test_name: str = '',
                                                 path_suffix_is_required_cases: Sequence[bool] = (False, True),
                                                 ):
        for path_suffix_is_required in path_suffix_is_required_cases:
            rel_opt_arg_conf = ARBITRARY_REL_OPT_ARG_CONF.config_for(path_suffix_is_required)
            for source_file_location in [None, Path('/source/file/location')]:
                with put.subTest(test_name=test_name,
                                 path_suffix_is_required=path_suffix_is_required,
                                 source_file_location=source_file_location):
                    token_stream = TokenStream(source_string)
                    with put.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.parse_path(token_stream,
                                       rel_opt_arg_conf,
                                       source_file_location=source_file_location)

    def __assertions_on_reference_restrictions(self,
                                               put: unittest.TestCase,
                                               actual: PathSdv,
                                               symbols: SymbolTable):
        for idx, reference in enumerate(actual.references):
            assert isinstance(reference, SymbolReference)  # Type info for IDE
            container = symbols.lookup(reference.name)
            assert isinstance(container, SymbolContainer)
            result = reference.restrictions.is_satisfied_by(symbols,
                                                            reference.name,
                                                            container)
            put.assertIsNone(result,
                             'Restriction on reference #{}: expects None=satisfaction'.format(idx))

    def __assertions_on_hypothetical_reference_to_sdv(
            self,
            put: unittest.TestCase,
            actual: PathSdv,
            symbols: SymbolTable):
        restriction = PathAndRelativityRestriction(PathRelativityVariants(RelOptionType, True))
        container = PathSymbolValueContext.of_sdv(actual).container
        result = restriction.is_satisfied_by(symbols, 'hypothetical_symbol', container)
        put.assertIsNone(result,
                         'Result of hypothetical restriction on path')


CHECKER = Checker()
