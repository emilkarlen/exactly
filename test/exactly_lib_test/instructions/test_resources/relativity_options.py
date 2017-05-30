import pathlib

from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelNonHomeOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.utils.arg_parse.test_resources import rel_symbol_arg_str
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForRelOptionType
from exactly_lib_test.test_case_file_structure.test_resources.non_home_populator import NonHomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class SymbolsConfiguration:
    """
    Configuration of symbols used by a relativity option (for a path cli argument).
    """

    def usage_expectation_assertions(self) -> list:
        return []

    def entries_for_arrangement(self) -> list:
        return []

    def usages_expectation(self) -> asrt.ValueAssertion:
        return asrt.matches_sequence(self.usage_expectation_assertions())

    def in_arrangement(self) -> SymbolTable:
        return symbol_utils.symbol_table_from_entries(self.entries_for_arrangement())


class OptionStringConfiguration:
    """
    Configuration for the relativity option (for a path cli argument).
    """

    def __init__(self, cli_option_string: str):
        self._cli_option_string = cli_option_string

    @property
    def option_string(self) -> str:
        return self._cli_option_string

    def __str__(self):
        return '{}(option_string={})'.format(type(self),
                                             self._cli_option_string)


class OptionStringConfigurationForDefaultRelativity(OptionStringConfiguration):
    def __init__(self):
        super().__init__('')


class OptionStringConfigurationForRelativityOption(OptionStringConfiguration):
    def __init__(self, relativity: RelOptionType):
        super().__init__(
            option_syntax.long_option_syntax(relative_path_options.REL_OPTIONS_MAP[relativity].option_name.long))


class OptionStringConfigurationForRelativityOptionRelNonHome(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelNonHomeOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_non_home(relativity))


class OptionStringConfigurationForRelativityOptionRelSds(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelSdsOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_sds(relativity))


class OptionStringConfigurationForRelSymbol(OptionStringConfiguration):
    def __init__(self, symbol_name: str):
        super().__init__(rel_symbol_arg_str(symbol_name))


class RelativityOptionConfiguration:
    """
    Complete Configuration of a relativity option (for a path cli argument). 
    """

    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        self._cli_option = cli_option
        self._symbols_configuration = symbols_configuration
        if not isinstance(cli_option, OptionStringConfiguration):
            raise ValueError('Not a OptionStringConfiguration: {}', cli_option)
        if not isinstance(symbols_configuration, SymbolsConfiguration):
            raise ValueError('Not a SymbolsConfiguration: {}', symbols_configuration)

    @property
    def option_string(self) -> str:
        return self._cli_option.option_string

    @property
    def test_case_description(self) -> str:
        return str(self._cli_option)

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    @property
    def symbols(self) -> SymbolsConfiguration:
        return self._symbols_configuration


class RelativityOptionConfigurationBase(RelativityOptionConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option, symbols_configuration)
        self.relativity = relativity
        self.resolver = relative_path_options.REL_OPTIONS_MAP[self.relativity].root_resolver
        if not isinstance(relativity, RelOptionType):
            raise ValueError('Not a RelOptionType: {}'.format(relativity))

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolver.exists_pre_sds

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForRelOptionType(self.relativity, contents)


class RelativityOptionConfigurationForRelNonHome(RelativityOptionConfiguration):
    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option,
                         symbols_configuration)

    def root_dir__non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def populator_for_relativity_option_root__non_home(self, contents: DirContents) -> NonHomePopulator:
        raise NotImplementedError()

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        raise NotImplementedError()


class RelativityOptionConfigurationForRelNonHomeBase(RelativityOptionConfigurationForRelNonHome):
    def __init__(self,
                 relativity: RelNonHomeOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option, symbols_configuration)
        self.relativity_non_home = relativity
        self.relativity = path_relativity.rel_any_from_rel_non_home(relativity)
        self.resolver_non_home = relative_path_options.REL_NON_HOME_OPTIONS_MAP[relativity].root_resolver

    @property
    def exists_pre_sds(self) -> bool:
        return False

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForRelOptionType(self.relativity, contents)

    def root_dir__non_home(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_non_home.from_non_home(sds)

    def populator_for_relativity_option_root__non_home(self, contents: DirContents) -> NonHomePopulator:
        return non_home_populator.rel_option(self.relativity_non_home, contents)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_non_home.from_non_home(sds)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        if self.relativity_non_home is RelNonHomeOptionType.REL_CWD:
            return sds_populator.cwd_contents(contents)
        else:
            relativity_sds = RelSdsOptionType(self.relativity_non_home.value)
            return sds_populator.contents_in(relativity_sds, contents)


class RelativityOptionConfigurationForRelSds(RelativityOptionConfigurationForRelNonHomeBase):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(path_relativity.rel_non_home_from_rel_sds(relativity),
                         cli_option,
                         symbols_configuration)
        self.relativity_sds = relativity
        self.resolver_sds = relative_path_options.REL_SDS_OPTIONS_MAP[relativity].root_resolver

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_sds.from_sds(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in(self.relativity_sds, contents)


class SymbolsConfigurationForSinglePathSymbol(SymbolsConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str):
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name

    def usage_expectation_assertions(self) -> list:
        return [
            equals_symbol_reference(
                self.symbol_name,
                equals_file_ref_relativity_restriction(
                    FileRefRelativityRestriction(self.expected_accepted_relativities)))

        ]

    def entries_for_arrangement(self) -> list:
        return [
            symbol_utils.entry(self.symbol_name,
                               FileRefConstant(file_refs.of_rel_option(self.relativity,
                                                                       PathPartAsNothing())))
        ]


def conf_rel_any(relativity: RelOptionType) -> RelativityOptionConfiguration:
    return RelativityOptionConfigurationBase(
        relativity,
        OptionStringConfigurationForRelativityOption(relativity))


def default_conf_rel_any(relativity: RelOptionType) -> RelativityOptionConfiguration:
    return RelativityOptionConfigurationBase(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_any(relativity: RelOptionType,
                        symbol_name: str,
                        accepted_relativities: PathRelativityVariants) -> RelativityOptionConfiguration:
    return RelativityOptionConfigurationBase(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(relativity,
                                                accepted_relativities,
                                                symbol_name))


def conf_rel_non_home(relativity: RelNonHomeOptionType) -> RelativityOptionConfigurationForRelNonHome:
    return RelativityOptionConfigurationForRelNonHomeBase(
        relativity,
        OptionStringConfigurationForRelativityOptionRelNonHome(relativity))


def default_conf_rel_non_home(relativity: RelNonHomeOptionType) -> RelativityOptionConfigurationForRelNonHome:
    return RelativityOptionConfigurationForRelNonHomeBase(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_non_home(relativity: RelNonHomeOptionType,
                             symbol_name: str,
                             accepted_relativities: PathRelativityVariants) -> RelativityOptionConfigurationForRelNonHome:
    return RelativityOptionConfigurationForRelNonHomeBase(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(path_relativity.rel_any_from_rel_non_home(relativity),
                                                accepted_relativities,
                                                symbol_name))


def conf_rel_sds(relativity: RelSdsOptionType) -> RelativityOptionConfigurationForRelSds:
    return RelativityOptionConfigurationForRelSds(
        relativity,
        OptionStringConfigurationForRelativityOptionRelSds(relativity))


def default_conf_rel_sds(relativity: RelSdsOptionType) -> RelativityOptionConfigurationForRelSds:
    return RelativityOptionConfigurationForRelSds(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_sds(relativity: RelSdsOptionType,
                        symbol_name: str,
                        accepted_relativities: PathRelativityVariants) -> RelativityOptionConfigurationForRelSds:
    return RelativityOptionConfigurationForRelSds(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(path_relativity.rel_any_from_rel_sds(relativity),
                                                accepted_relativities,
                                                symbol_name)
    )
