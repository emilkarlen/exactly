import pathlib
from abc import ABC
from typing import List, Sequence

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.path_sdv_impls.constant import PathConstantSdv
from exactly_lib.symbol.data.restrictions.value_restrictions import PathRelativityRestriction
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.test_case_file_structure import path_relativity
from exactly_lib.test_case_file_structure import relative_path_options
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelNonHdsOptionType, RelHdsOptionType, DirectoryStructurePartition, rel_any_from_rel_sds
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP, REL_NON_HDS_OPTIONS_MAP
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.data.concrete_path_parts import PathPartDdvAsFixedPath
from exactly_lib.type_system.data.path_part import PathPartDdv
from exactly_lib.type_system.data.paths import empty_path_part
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_path_relativity_restriction
from exactly_lib_test.symbol.data.test_resources.path import PathDdvSymbolContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import \
    matches_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources import non_hds_populator
from exactly_lib_test.test_case_file_structure.test_resources import path_arguments as path_args, sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.non_hds_populator import NonHdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_contents_check
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import \
    TcdsPopulator, \
    TcdsPopulatorForRelOptionType
from exactly_lib_test.test_resources import arguments_building
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SymbolsConfiguration:
    """
    Configuration of symbols used by a relativity option (for a path cli argument).
    """

    def reference_expectation_assertions(self) -> List[ValueAssertion[SymbolReference]]:
        return []

    def usage_expectation_assertions(self) -> List[ValueAssertion[SymbolUsage]]:
        return self.reference_expectation_assertions()

    def contexts_for_arrangement(self) -> List[SymbolContext]:
        return []

    def usages_expectation(self) -> ValueAssertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(self.reference_expectation_assertions())

    def in_arrangement(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.contexts_for_arrangement())


class NamedFileConf:
    def __init__(self,
                 name: str,
                 sdv: PathSdv,
                 cl_argument: PathArgument,
                 ):
        self._name = name
        self._sdv = sdv
        self._cl_argument = cl_argument

    @property
    def name(self) -> str:
        return self._name

    @property
    def path_sdv(self) -> PathSdv:
        return self._sdv

    @property
    def cl_argument(self) -> PathArgument:
        return self._cl_argument


class OptionStringConfiguration:
    """
    Configuration for the relativity option (for a path cli argument).
    """

    def __init__(self, argument: ArgumentElementsRenderer):
        self._argument = argument

    @property
    def argument(self) -> ArgumentElementsRenderer:
        return self._argument

    @property
    def option_string(self) -> str:
        return str(self.argument)

    def file_argument(self, file_name: str) -> PathArgument:
        return path_args.path_argument(file_name, self.argument)

    def __str__(self):
        return '{}(option_string={})'.format(type(self),
                                             self.option_string)


class OptionStringConfigurationForDefaultRelativity(OptionStringConfiguration):
    def __init__(self):
        super().__init__(arguments_building.EmptyArgument())


class OptionStringConfigurationForRelativityOption(OptionStringConfiguration):
    def __init__(self, relativity: RelOptionType):
        super().__init__(path_args.rel_option_type_arg(relativity))
        self._relativity = relativity

    @property
    def rel_option_type(self) -> RelOptionType:
        return self._relativity


class OptionStringConfigurationForRelativityOptionRelHds(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelHdsOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_hds(relativity))


class OptionStringConfigurationForRelativityOptionRelNonHds(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelNonHdsOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_non_hds(relativity))


class OptionStringConfigurationForRelativityOptionRelSds(OptionStringConfigurationForRelativityOption):
    def __init__(self, relativity: RelSdsOptionType):
        super().__init__(
            path_relativity.rel_any_from_rel_sds(relativity))


class OptionStringConfigurationForRelSymbol(OptionStringConfiguration):
    def __init__(self, symbol_name: str):
        super().__init__(path_args.rel_symbol_arg(symbol_name))


class RelativityOptionConfiguration(ABC):
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

    def path_sdv_for_root_dir(self) -> PathSdv:
        raise NotImplementedError('abstract method')

    def path_sdv_for(self, file_name: str = '') -> PathSdv:
        raise NotImplementedError('abstract method')

    @property
    def cli_option_conf(self) -> OptionStringConfiguration:
        return self._cli_option

    @property
    def option_string(self) -> str:
        return self._cli_option.option_string

    def named_file_conf(self, file_name: str) -> NamedFileConf:
        return NamedFileConf(file_name,
                             self.path_sdv_for(file_name),
                             self._cli_option.file_argument(file_name))

    @property
    def option_argument(self) -> ArgumentElementsRenderer:
        return self._cli_option.argument

    def path_argument_of_rel_name(self, file_name: str) -> PathArgument:
        return path_args.path_argument(file_name, self._cli_option.argument)

    @property
    def option_argument_str(self) -> str:
        return str(self._cli_option.argument)

    @property
    def test_case_description(self) -> str:
        return str(self._cli_option)

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        raise NotImplementedError()

    def population_dir(self, tds: Tcds) -> pathlib.Path:
        raise NotImplementedError()

    @property
    def symbols(self) -> SymbolsConfiguration:
        return self._symbols_configuration


class RelativityOptionConfigurationForRelOptionType(RelativityOptionConfiguration, ABC):
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

    def path_sdv_for_root_dir(self) -> PathSdv:
        return path_sdvs.constant(
            paths.of_rel_option(self.relativity_option,
                                empty_path_part())
        )

    def path_sdv_for(self, file_name: str = '') -> PathSdv:
        return path_sdvs.constant(
            paths.of_rel_option(self.relativity_option,
                                _empty_or_fixed_path_part(file_name))
        )

    @property
    def is_rel_cwd(self) -> bool:
        return self.relativity_option == RelOptionType.REL_CWD

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolver.exists_pre_sds

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        return TcdsPopulatorForRelOptionType(self.relativity, contents)

    def population_dir(self, tds: Tcds) -> pathlib.Path:
        return REL_OPTIONS_MAP[self.relativity].root_resolver.from_tcds(tds)


class RelativityOptionConfigurationRelHds(RelativityOptionConfigurationForRelOptionType):
    def __init__(self,
                 relativity: RelHdsOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(path_relativity.rel_any_from_rel_hds(relativity),
                         cli_option,
                         symbols_configuration)
        self._relativity_hds = relativity
        self._resolver_hds = relative_path_options.REL_HDS_OPTIONS_MAP[relativity].root_resolver

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return DirectoryStructurePartition.HDS

    @property
    def relativity_option_rel_hds(self) -> RelHdsOptionType:
        return self._relativity_hds

    def root_dir__hds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self._resolver_hds.from_hds(hds)

    def populator_for_relativity_option_root__hds(self, contents: DirContents) -> HdsPopulator:
        return hds_populators.contents_in(self._relativity_hds, contents)

    @property
    def exists_pre_sds(self) -> bool:
        return True


class RelativityOptionConfigurationForRelNonHds(RelativityOptionConfiguration):
    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option,
                         symbols_configuration)

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return DirectoryStructurePartition.NON_HDS

    def root_dir__non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def populator_for_relativity_option_root__non_hds(self, contents: DirContents) -> NonHdsPopulator:
        raise NotImplementedError()

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        raise NotImplementedError()

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> ValueAssertion:
        raise NotImplementedError('abstract method')


class RelativityOptionConfigurationForRelNonHdsBase(RelativityOptionConfigurationForRelNonHds):
    def __init__(self,
                 relativity: RelNonHdsOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option, symbols_configuration)
        self.relativity_non_hds = relativity
        self.relativity = path_relativity.rel_any_from_rel_non_hds(relativity)
        self.resolver_non_hds = relative_path_options.REL_NON_HDS_OPTIONS_MAP[relativity].root_resolver

    @property
    def exists_pre_sds(self) -> bool:
        return False

    @property
    def is_rel_cwd(self) -> bool:
        return self.relativity_non_hds == RelNonHdsOptionType.REL_CWD

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        return TcdsPopulatorForRelOptionType(self.relativity, contents)

    def root_dir__non_hds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_non_hds.from_non_hds(sds)

    def populator_for_relativity_option_root__non_hds(self, contents: DirContents) -> NonHdsPopulator:
        return non_hds_populator.rel_option(self.relativity_non_hds, contents)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_non_hds.from_non_hds(sds)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        if self.relativity_non_hds is RelNonHdsOptionType.REL_CWD:
            return sds_populator.cwd_contents(contents)
        else:
            relativity_sds = RelSdsOptionType(self.relativity_non_hds.value)
            return sds_populator.contents_in(relativity_sds, contents)

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> ValueAssertion:
        return sds_contents_check.non_hds_dir_contains_exactly(self.root_dir__non_hds,
                                                               contents)

    def population_dir(self, tds: Tcds) -> pathlib.Path:
        return REL_NON_HDS_OPTIONS_MAP[self.relativity_non_hds].root_resolver.from_tcds(tds)


class RelativityOptionConfigurationForRelSds(RelativityOptionConfigurationForRelNonHdsBase):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(path_relativity.rel_non_hds_from_rel_sds(relativity),
                         cli_option,
                         symbols_configuration)
        self.relativity_sds = relativity
        self.resolver_sds = relative_path_options.REL_SDS_OPTIONS_MAP[relativity].root_resolver

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return self.resolver_sds.from_sds(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in(self.relativity_sds, contents)

    def path_sdv_for_root_dir(self) -> PathSdv:
        return PathConstantSdv(paths.of_rel_option(rel_any_from_rel_sds(self.relativity_sds),
                                                   empty_path_part()))

    def path_sdv_for(self, file_name: str = '') -> PathSdv:
        return PathConstantSdv(paths.of_rel_option(rel_any_from_rel_sds(self.relativity_sds),
                                                   _empty_or_fixed_path_part(file_name)))


class SymbolsConfigurationForSinglePathSymbol(SymbolsConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str):
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name
        self.symbol_context = PathDdvSymbolContext(symbol_name,
                                                   paths.of_rel_option(relativity,
                                                                       paths.empty_path_part()),
                                                   )

    def reference_expectation_assertions(self) -> List[ValueAssertion[SymbolReference]]:
        return [
            matches_symbol_reference_with_restriction_on_direct_target(
                self.symbol_name,
                equals_path_relativity_restriction(
                    PathRelativityRestriction(self.expected_accepted_relativities)))

        ]

    def contexts_for_arrangement(self) -> List[SymbolContext]:
        return [self.symbol_context]


def conf_rel_any(relativity: RelOptionType) -> RelativityOptionConfigurationForRelOptionType:
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


def conf_rel_non_hds(relativity: RelNonHdsOptionType) -> RelativityOptionConfigurationForRelNonHds:
    return RelativityOptionConfigurationForRelNonHdsBase(
        relativity,
        OptionStringConfigurationForRelativityOptionRelNonHds(relativity))


def default_conf_rel_non_hds(relativity: RelNonHdsOptionType) -> RelativityOptionConfigurationForRelNonHds:
    return RelativityOptionConfigurationForRelNonHdsBase(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_non_hds(relativity: RelNonHdsOptionType,
                            symbol_name: str,
                            accepted_relativities: PathRelativityVariants
                            ) -> RelativityOptionConfigurationForRelNonHds:
    return RelativityOptionConfigurationForRelNonHdsBase(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(path_relativity.rel_any_from_rel_non_hds(relativity),
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


def conf_rel_hds(relativity: RelHdsOptionType) -> RelativityOptionConfigurationRelHds:
    return RelativityOptionConfigurationRelHds(
        relativity,
        OptionStringConfigurationForRelativityOptionRelHds(relativity))


def every_conf_rel_hds() -> List[RelativityOptionConfigurationRelHds]:
    return [
        conf_rel_hds(relativity)
        for relativity in RelHdsOptionType
    ]


def default_conf_rel_hds(relativity: RelHdsOptionType) -> RelativityOptionConfigurationRelHds:
    return RelativityOptionConfigurationRelHds(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_hds(relativity: RelHdsOptionType,
                        symbol_name: str,
                        accepted_relativities: PathRelativityVariants) -> RelativityOptionConfigurationRelHds:
    return RelativityOptionConfigurationRelHds(
        relativity,
        OptionStringConfigurationForRelSymbol(symbol_name),
        SymbolsConfigurationForSinglePathSymbol(path_relativity.rel_any_from_rel_hds(relativity),
                                                accepted_relativities,
                                                symbol_name))


def _empty_or_fixed_path_part(file_name: str) -> PathPartDdv:
    if file_name and not file_name.isspace():
        return PathPartDdvAsFixedPath(file_name)
    else:
        return empty_path_part()
