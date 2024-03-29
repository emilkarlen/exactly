import pathlib
from abc import ABC
from typing import List, Sequence

from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.tcfs import path_relativity
from exactly_lib.tcfs import relative_path_options
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants, \
    RelSdsOptionType, RelNonHdsOptionType, RelHdsOptionType, DirectoryStructurePartition, rel_any_from_rel_sds
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP, REL_NON_HDS_OPTIONS_MAP
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.value_restrictions import PathAndRelativityRestriction
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.path.path_ddvs import empty_path_part
from exactly_lib.type_val_deps.types.path.path_part_ddv import PathPartDdv
from exactly_lib.type_val_deps.types.path.path_part_ddvs import PathPartDdvAsFixedPath
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import hds_populators
from exactly_lib_test.tcfs.test_resources import non_hds_populator
from exactly_lib_test.tcfs.test_resources import path_arguments as path_args, sds_populator
from exactly_lib_test.tcfs.test_resources.dir_populator import HdsPopulator
from exactly_lib_test.tcfs.test_resources.non_hds_populator import NonHdsPopulator
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.tcfs.test_resources.sds_check import sds_contents_check
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    TcdsPopulator, \
    TcdsPopulatorForRelOptionType
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, FileSystemElements
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import value_restriction_assertions as asrt_val_rest
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_reference_assertions import \
    matches_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import RelativityAbsStx, \
    PathWConstNameAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.references import PathReferenceVariant
from exactly_lib_test.type_val_deps.types.path.test_resources.symbol_context import PathDdvSymbolContext


class SymbolsConfiguration:
    """
    Configuration of symbols used by a relativity option (for a path cli argument).
    """

    def reference_expectation_assertions(self) -> List[Assertion[SymbolReference]]:
        return []

    def usage_expectation_assertions(self) -> List[Assertion[SymbolUsage]]:
        return self.reference_expectation_assertions()

    def contexts_for_arrangement(self) -> List[SymbolContext]:
        return []

    def usages_expectation(self) -> Assertion[Sequence[SymbolUsage]]:
        return asrt.matches_sequence(self.reference_expectation_assertions())

    def in_arrangement(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.contexts_for_arrangement())


class NamedFileConf:
    def __init__(self,
                 name: str,
                 sdv: PathSdv,
                 cl_argument: PathArgument,
                 abstract_syntax: PathWConstNameAbsStx,
                 ):
        self._name = name
        self._sdv = sdv
        self._cl_argument = cl_argument
        self._abstract_syntax = abstract_syntax

    @property
    def name(self) -> str:
        return self._name

    @property
    def path_sdv(self) -> PathSdv:
        return self._sdv

    @property
    def cl_argument(self) -> PathArgument:
        return self._cl_argument

    @property
    def abstract_syntax(self) -> PathWConstNameAbsStx:
        return self._abstract_syntax

    def file_with_contents(self, contents: str) -> File:
        return File(self._name, contents)


class OptionStringConfiguration:
    """
    Configuration for the relativity option (for a path cli argument).
    """

    def __init__(self,
                 argument: ArgumentElementsRenderer,
                 relativity_abs_stx: RelativityAbsStx,
                 ):
        self._argument = argument
        self._relativity_abs_stx = relativity_abs_stx

    @property
    def argument(self) -> ArgumentElementsRenderer:
        return self._argument

    @property
    def relativity_abs_stx(self) -> RelativityAbsStx:
        return self._relativity_abs_stx

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
        super().__init__(argument_renderer.EmptyArgument(),
                         path_abs_stx.DefaultRelativityAbsStx())


class OptionStringConfigurationForRelativityOption(OptionStringConfiguration):
    def __init__(self, relativity: RelOptionType):
        super().__init__(path_args.rel_option_type_arg(relativity),
                         path_abs_stx.OptionRelativityAbsStx(relativity))
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
        super().__init__(path_args.rel_symbol_arg(symbol_name),
                         path_abs_stx.SymbolRelativityAbsStx(symbol_name))


class RelativityOptionConfiguration(ABC):
    """
    Complete Configuration of a relativity option (for a path cli argument). 
    """

    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration(),
                 ):
        self._cli_option = cli_option
        self._symbols_configuration = symbols_configuration
        if not isinstance(cli_option, OptionStringConfiguration):
            raise ValueError('Not a {}: {}'.format(OptionStringConfiguration, cli_option))
        if not isinstance(symbols_configuration, SymbolsConfiguration):
            raise ValueError('Not a {}: {}'.format(SymbolsConfiguration, symbols_configuration))

    @property
    def name(self) -> str:
        """A name useful for inclusion in test case variant descriptions"""
        return 'cli_opt={cli_opt}, symbols={symbols}'.format(
            cli_opt=repr(self._cli_option.option_string),
            symbols=repr([
                symbol.name
                for symbol in self._symbols_configuration.contexts_for_arrangement()
            ])
        )

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        raise NotImplementedError('abstract method')

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    @property
    def is_rel_cwd(self) -> bool:
        raise NotImplementedError('abstract method')

    def path_sdv_for_root_dir(self) -> PathSdv:
        return self._path_sdv_for(empty_path_part())

    def path_sdv_for(self, file_name: str) -> PathSdv:
        return self._path_sdv_for(_empty_or_fixed_path_part(file_name))

    def _path_sdv_for(self, path_suffix: PathPartDdv) -> PathSdv:
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
                             self._cli_option.file_argument(file_name),
                             self.path_abs_stx_of_name(file_name))

    @property
    def option_argument(self) -> ArgumentElementsRenderer:
        return self._cli_option.argument

    def path_argument_of_rel_name(self, file_name: str) -> PathArgument:
        return path_args.path_argument(file_name, self._cli_option.argument)

    def path_abs_stx_of_name(self, file_name: str) -> PathWConstNameAbsStx:
        return path_abs_stx.PathWConstNameAbsStx(
            self._cli_option.relativity_abs_stx,
            file_name,
        )

    def path_abs_stx_of_name__c(self, file_name_components: Sequence[str]) -> PathWConstNameAbsStx:
        return self.path_abs_stx_of_name(
            path_abs_stx.file_name_from_components__str(file_name_components)
        )

    @property
    def option_argument_str(self) -> str:
        return str(self._cli_option.argument)

    @property
    def test_case_description(self) -> str:
        return str(self._cli_option)

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root__s(self, contents: FileSystemElements) -> TcdsPopulator:
        return self.populator_for_relativity_option_root(DirContents(contents))

    def population_dir(self, tds: TestCaseDs) -> pathlib.Path:
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
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return path_relativity.RESOLVING_DEPENDENCY_OF[self.relativity]

    @property
    def is_rel_cwd(self) -> bool:
        return self.relativity_option == RelOptionType.REL_CWD

    @property
    def exists_pre_sds(self) -> bool:
        return self.resolver.exists_pre_sds

    @property
    def relativity_option(self) -> RelOptionType:
        return self.relativity

    def _path_sdv_for(self, path_suffix: PathPartDdv) -> PathSdv:
        return path_sdvs.constant(
            path_ddvs.of_rel_option(self.relativity_option,
                                    path_suffix)
        )

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        return TcdsPopulatorForRelOptionType(self.relativity, contents)

    def population_dir(self, tds: TestCaseDs) -> pathlib.Path:
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

    def root_dir__hds(self, hds: HomeDs) -> pathlib.Path:
        return self._resolver_hds.from_hds(hds)

    def populator_for_relativity_option_root__hds(self, contents: DirContents) -> HdsPopulator:
        return hds_populators.contents_in(self._relativity_hds, contents)

    @property
    def exists_pre_sds(self) -> bool:
        return True


class RelativityOptionConfigurationForRelNonHds(RelativityOptionConfiguration, ABC):
    def __init__(self,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(cli_option,
                         symbols_configuration)

    @property
    def directory_structure_partition(self) -> DirectoryStructurePartition:
        return DirectoryStructurePartition.NON_HDS

    def root_dir__non_hds(self, sds: SandboxDs) -> pathlib.Path:
        raise NotImplementedError()

    def populator_for_relativity_option_root__non_hds(self, contents: DirContents) -> NonHdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root__non_hds__s(self, contents: FileSystemElements) -> NonHdsPopulator:
        return self.populator_for_relativity_option_root__non_hds(DirContents(contents))

    # TODO Should not exist in this class - exists due to bad design
    def root_dir__sds(self, sds: SandboxDs) -> pathlib.Path:
        raise NotImplementedError()

    # TODO Should not exist in this class - exists due to bad design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        raise NotImplementedError()

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> Assertion[SandboxDs]:
        raise NotImplementedError('abstract method')

    def assert_root_dir_contains_exactly__p(self, contents: FileSystemElements) -> Assertion[SandboxDs]:
        return self.assert_root_dir_contains_exactly(DirContents(contents))


class RelativityOptionConfigurationForRelNonHdsImpl(RelativityOptionConfigurationForRelNonHds):
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

    def _path_sdv_for(self, path_suffix: PathPartDdv) -> PathSdv:
        return path_sdvs.constant(
            path_ddvs.of_rel_option(self.relativity,
                                    path_suffix)
        )

    def populator_for_relativity_option_root(self, contents: DirContents) -> TcdsPopulator:
        return TcdsPopulatorForRelOptionType(self.relativity, contents)

    def root_dir__non_hds(self, sds: SandboxDs) -> pathlib.Path:
        return self.resolver_non_hds.from_non_hds(sds)

    def populator_for_relativity_option_root__non_hds(self, contents: DirContents) -> NonHdsPopulator:
        return non_hds_populator.rel_option(self.relativity_non_hds, contents)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def root_dir__sds(self, sds: SandboxDs) -> pathlib.Path:
        return self.resolver_non_hds.from_non_hds(sds)

    # TODO ska inte finnas i denna klass - finns pga felaktig design
    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        if self.relativity_non_hds is RelNonHdsOptionType.REL_CWD:
            return sds_populator.cwd_contents(contents)
        else:
            relativity_sds = RelSdsOptionType(self.relativity_non_hds.value)
            return sds_populator.contents_in(relativity_sds, contents)

    def populator_for_relativity_option_root__sds__s(self, contents: FileSystemElements) -> sds_populator.SdsPopulator:
        return self.populator_for_relativity_option_root__sds(DirContents(contents))

    def assert_root_dir_contains_exactly(self, contents: DirContents) -> Assertion[SandboxDs]:
        return sds_contents_check.non_hds_dir_contains_exactly(self.root_dir__non_hds,
                                                               contents)

    def population_dir(self, tds: TestCaseDs) -> pathlib.Path:
        return REL_NON_HDS_OPTIONS_MAP[self.relativity_non_hds].root_resolver.from_tcds(tds)


class RelativityOptionConfigurationForRelSds(RelativityOptionConfigurationForRelNonHdsImpl):
    def __init__(self,
                 relativity: RelSdsOptionType,
                 cli_option: OptionStringConfiguration,
                 symbols_configuration: SymbolsConfiguration = SymbolsConfiguration()):
        super().__init__(path_relativity.rel_non_hds_from_rel_sds(relativity),
                         cli_option,
                         symbols_configuration)
        self.relativity_sds = relativity
        self.resolver_sds = relative_path_options.REL_SDS_OPTIONS_MAP[relativity].root_resolver

    def root_dir__sds(self, sds: SandboxDs) -> pathlib.Path:
        return self.resolver_sds.from_sds(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in(self.relativity_sds, contents)

    def _path_sdv_for(self, path_suffix: PathPartDdv) -> PathSdv:
        return path_sdvs.constant(
            path_ddvs.of_rel_option(rel_any_from_rel_sds(self.relativity_sds),
                                    path_suffix)
        )


class SymbolsConfigurationForSinglePathSymbol(SymbolsConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str):
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name
        self.symbol_context = PathDdvSymbolContext(symbol_name,
                                                   path_ddvs.of_rel_option(relativity,
                                                                           path_ddvs.empty_path_part()),
                                                   accepted_relativities=expected_accepted_relativities,
                                                   default_reference_variant=PathReferenceVariant.PATH,
                                                   )

    def reference_expectation_assertions(self) -> List[Assertion[SymbolReference]]:
        return [
            matches_symbol_reference_with_restriction_on_direct_target(
                self.symbol_name,
                asrt_val_rest.equals__path_w_relativity(
                    PathAndRelativityRestriction(self.expected_accepted_relativities))
            )
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
    return RelativityOptionConfigurationForRelNonHdsImpl(
        relativity,
        OptionStringConfigurationForRelativityOptionRelNonHds(relativity))


def default_conf_rel_non_hds(relativity: RelNonHdsOptionType) -> RelativityOptionConfigurationForRelNonHds:
    return RelativityOptionConfigurationForRelNonHdsImpl(
        relativity,
        OptionStringConfigurationForDefaultRelativity())


def symbol_conf_rel_non_hds(relativity: RelNonHdsOptionType,
                            symbol_name: str,
                            accepted_relativities: PathRelativityVariants
                            ) -> RelativityOptionConfigurationForRelNonHds:
    return RelativityOptionConfigurationForRelNonHdsImpl(
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
