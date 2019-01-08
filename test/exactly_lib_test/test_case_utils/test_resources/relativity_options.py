import pathlib
from typing import List, Sequence

from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.file_ref_resolver_impls.constant import FileRefConstant
from exactly_lib.symbol.data.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolUsage
from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelNonHomeOptionType, RelHomeOptionType, DirectoryStructurePartition, rel_any_from_rel_sds
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP, REL_NON_HOME_OPTIONS_MAP
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.data.file_refs import empty_path_part
from exactly_lib.type_system.data.path_part import PathPart
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.test_case_file_structure.test_resources import arguments_building as file_ref_args, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import FileRefArgument
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_populators import \
    HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForRelOptionType
from exactly_lib_test.test_case_file_structure.test_resources.non_home_populator import NonHomePopulator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_contents_check
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.test_resources import symbol_tables


class SymbolsConfiguration:
    """
    Configuration of symbols used by a relativity option (for a path cli argument).
    """

    def usage_expectation_assertions(self) -> List[ValueAssertion[SymbolReference]]:
        return []

    def entries_for_arrangement(self) -> List[Entry]:
        return []

    def usages_expectation(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(self.usage_expectation_assertions())

    def in_arrangement(self) -> SymbolTable:
        return symbol_tables.symbol_table_from_entries(self.entries_for_arrangement())


class NamedFileConf:
    def __init__(self,
                 name: str,
                 resolver: FileRefResolver,
                 cl_argument: FileRefArgument,
                 ):
        self._name = name
        self._resolver = resolver
        self._cl_argument = cl_argument

    @property
    def name(self) -> str:
        return self._name

    @property
    def file_ref_resolver(self) -> FileRefResolver:
        return self._resolver

    @property
    def cl_argument(self) -> FileRefArgument:
        return self._cl_argument


class OptionStringConfiguration:
    """
    Configuration for the relativity option (for a path cli argument).
    """

    def __init__(self, argument: ArgumentElementRenderer):
        self._argument = argument

    @property
    def argument(self) -> ArgumentElementRenderer:
        return self._argument

    @property
    def option_string(self) -> str:
        return str(self.argument)

    def file_argument(self, file_name: str) -> FileRefArgument:
        return FileRefArgument(file_name, self.argument)

    def __str__(self):
        return '{}(option_string={})'.format(type(self),
                                             self.option_string)


class OptionStringConfigurationForDefaultRelativity(OptionStringConfiguration):
    def __init__(self):
        super().__init__(arguments_building.EmptyArgument())


class OptionStringConfigurationForRelativityOption(OptionStringConfiguration):
    def __init__(self, relativity: RelOptionType):
        super().__init__(file_ref_args.rel_option_type_arg(relativity))
        self._relativity = relativity

    @property
    def rel_option_type(self) -> RelOptionType:
        return self._relativity


class OptionStringConfigurationForRelativityOptionRelHome(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelHomeOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_home(relativity))


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
        super().__init__(file_ref_args.rel_symbol_arg(symbol_name))


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
            raise ValueError('Not a {}: {}'.format(OptionStringConfiguration, cli_option))
        if not isinstance(symbols_configuration, SymbolsConfiguration):
            raise ValueError('Not a {}: {}'.format(SymbolsConfiguration, symbols_configuration))

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        raise NotImplementedError('abstract method')

    @property
    def is_rel_cwd(self) -> bool:
        raise NotImplementedError('abstract method')

    def file_ref_resolver_for(self, file_name: str = '') -> FileRefResolver:
        raise NotImplementedError('abstract method')

    @property
    def cli_option_conf(self) -> OptionStringConfiguration:
        return self._cli_option

    @property
    def option_string(self) -> str:
        return self._cli_option.option_string

    def named_file_conf(self, file_name: str) -> NamedFileConf:
        return NamedFileConf(file_name,
                             self.file_ref_resolver_for(file_name),
                             self._cli_option.file_argument(file_name))

    @property
    def option_argument(self) -> ArgumentElementRenderer:
        return self._cli_option.argument

    def file_argument_with_option(self, file_name: str) -> FileRefArgument:
        return FileRefArgument(file_name, self._cli_option.argument)

    @property
    def option_argument_str(self) -> str:
        return str(self._cli_option.argument)

    @property
    def test_case_description(self) -> str:
        return str(self._cli_option)

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def population_dir(self, tds: HomeAndSds) -> pathlib.Path:
        raise NotImplementedError()

    @property
    def symbols(self) -> SymbolsConfiguration:
        return self._symbols_configuration


class RelativityOptionConfigurationForRelOptionType(RelativityOptionConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option, symbols_configuration)
        self._relativity = relativity
        self.resolver = relative_path_options.REL_OPTIONS_MAP[self.relativity].root_resolver
        if not isinstance(relativity, RelOptionType):
            raise ValueError('Not a RelOptionType: {}'.format(relativity))

    @property
    def relativity(self) -> RelOptionType:
        return self._relativity

    @property
    def relativity_option(self) -> RelOptionType:
        return self.relativity

    def file_ref_resolver_for(self, file_name: str = '') -> FileRefResolver:
        return file_ref_resolvers.constant(
            file_refs.of_rel_option(self.relativity_option,
                                    _empty_or_fixed_path_part(file_name))
        )

    @property
    def is_rel_cwd(self) -> bool:
        return self.relativity_option == RelOptionType.REL_CWD

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolver.exists_pre_sds

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForRelOptionType(self.relativity, contents)

    def population_dir(self, tds: HomeAndSds) -> pathlib.Path:
        return REL_OPTIONS_MAP[self.relativity].root_resolver.from_home_and_sds(tds)


class RelativityOptionConfigurationRelHome(RelativityOptionConfigurationForRelOptionType):
    def __init__(self,
                 relativity: RelHomeOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(path_relativity.rel_any_from_rel_home(relativity),
                         cli_option,
                         symbols_configuration)
        self._relativity_hds = relativity
        self._resolver_hds = relative_path_options.REL_HOME_OPTIONS_MAP[relativity].root_resolver

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return DirectoryStructurePartition.HOME

    @property
    def relativity_option_rel_home(self) -> RelHomeOptionType:
        return self._relativity_hds

    def root_dir__hds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self._resolver_hds.from_home(hds)

    def populator_for_relativity_option_root__home(self, contents: DirContents) -> HomePopulator:
        return home_populators.contents_in(self._relativity_hds, contents)

    @property
    def exists_pre_sds(self) -> bool:
        return True


class RelativityOptionConfigurationForRelNonHome(RelativityOptionConfiguration):
    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option,
                         symbols_configuration)

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return DirectoryStructurePartition.NON_HOME

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

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> ValueAssertion:
        raise NotImplementedError('abstract method')


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

    @property
    def is_rel_cwd(self) -> bool:
        return self.relativity_non_home == RelNonHomeOptionType.REL_CWD

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

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> ValueAssertion:
        return sds_contents_check.non_home_dir_contains_exactly(self.root_dir__non_home,
                                                                contents)

    def population_dir(self, tds: HomeAndSds) -> pathlib.Path:
        return REL_NON_HOME_OPTIONS_MAP[self.relativity_non_home].root_resolver.from_home_and_sds(tds)


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

    def file_ref_resolver_for(self, file_name: str = '') -> FileRefResolver:
        return FileRefConstant(file_refs.of_rel_option(rel_any_from_rel_sds(self.relativity_sds),
                                                       _empty_or_fixed_path_part(file_name)))


class SymbolsConfigurationForSinglePathSymbol(SymbolsConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str):
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name

    def usage_expectation_assertions(self) -> List[ValueAssertion[SymbolReference]]:
        return [
            equals_symbol_reference_with_restriction_on_direct_target(
                self.symbol_name,
                equals_file_ref_relativity_restriction(
                    FileRefRelativityRestriction(self.expected_accepted_relativities)))

        ]

    def entries_for_arrangement(self) -> List[Entry]:
        return [
            data_symbol_utils.entry(
                self.symbol_name,
                file_ref_resolvers.constant(
                    file_refs.of_rel_option(self.relativity,
                                            file_refs.empty_path_part())))
        ]


def conf_rel_any(relativity: RelOptionType) -> RelativityOptionConfiguration:
    return RelativityOptionConfigurationForRelOptionType(
        relativity,
        OptionStringConfigurationForRelativityOption(relativity))


def default_conf_rel_any(relativity: RelOptionType) -> RelativityOptionConfigurationForRelOptionType:
    return RelativityOptionConfigurationForRelOptionType(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_any(relativity: RelOptionType,
                        symbol_name: str,
                        accepted_relativities: PathRelativityVariants) -> RelativityOptionConfigurationForRelOptionType:
    return RelativityOptionConfigurationForRelOptionType(
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
                             accepted_relativities: PathRelativityVariants
                             ) -> RelativityOptionConfigurationForRelNonHome:
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


def conf_rel_home(relativity: RelHomeOptionType) -> RelativityOptionConfigurationRelHome:
    return RelativityOptionConfigurationRelHome(
        relativity,
        OptionStringConfigurationForRelativityOptionRelHome(relativity))


def every_conf_rel_home() -> List[RelativityOptionConfigurationRelHome]:
    return [
        conf_rel_home(relativity)
        for relativity in RelHomeOptionType
    ]


def default_conf_rel_home(relativity: RelHomeOptionType) -> RelativityOptionConfigurationRelHome:
    return RelativityOptionConfigurationRelHome(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_home(relativity: RelHomeOptionType,
                         symbol_name: str,
                         accepted_relativities: PathRelativityVariants) -> RelativityOptionConfigurationRelHome:
    return RelativityOptionConfigurationRelHome(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(path_relativity.rel_any_from_rel_home(relativity),
                                                accepted_relativities,
                                                symbol_name))


def _empty_or_fixed_path_part(file_name: str) -> PathPart:
    if file_name and not file_name.isspace():
        return PathPartAsFixedPath(file_name)
    else:
        return empty_path_part()
