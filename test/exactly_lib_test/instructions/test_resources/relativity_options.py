import pathlib

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsNothing
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check, pfh_check
from exactly_lib_test.instructions.utils.arg_parse.test_resources import rel_symbol_arg_str
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulator, \
    HomeOrSdsPopulatorForHomeContents, HomeOrSdsPopulatorForSdsContents, HomeOrSdsPopulatorForRelOptionType
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsPopulator
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class RelativityOptionConfiguration:
    def __init__(self, cli_option: str):
        self._cli_option = cli_option

    @property
    def option_string(self) -> str:
        return self._cli_option

    @property
    def test_case_description(self) -> str:
        return self._cli_option

    @property
    def exists_pre_sds(self) -> bool:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root_for_contents_from_fun(self,
                                                                   file_name: str,
                                                                   home_and_sds_2_file_contents_str
                                                                   ) -> HomeOrSdsPopulator:
        return _HomeOrSdsPopulatorForContentsThatDependOnHomeAndSds(file_name,
                                                                    home_and_sds_2_file_contents_str,
                                                                    self.populator_for_relativity_option_root)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        raise NotImplementedError()

    def symbol_entries_for_arrangement(self) -> list:
        return []

    def symbols_in_arrangement(self) -> SymbolTable:
        return symbol_utils.symbol_table_from_entries(self.symbol_entries_for_arrangement())

    def symbol_usage_expectation_assertions(self) -> list:
        return []

    def symbol_usages_expectation(self) -> asrt.ValueAssertion:
        return asrt.matches_sequence(self.symbol_usage_expectation_assertions())


class RelativityOptionConfigurationForRelSymbol(RelativityOptionConfiguration):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str = 'SYMBOL_NAME'):
        super().__init__(rel_symbol_arg_str(symbol_name))
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name
        self.helper = SymbolsRelativityHelper(relativity, expected_accepted_relativities, symbol_name)

    @property
    def test_case_description(self) -> str:
        return self._cli_option + '/' + str(self.relativity)

    @property
    def exists_pre_sds(self) -> bool:
        return self.relativity is RelOptionType.REL_HOME

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        if self.relativity is RelOptionType.REL_HOME:
            return Expectation(
                validation_pre_sds=svh_check.is_validation_error(),
                symbol_usages=self.symbol_usages_expectation(),
            )
        else:
            return Expectation(
                main_result=pfh_check.is_fail(),
                symbol_usages=self.symbol_usages_expectation(),
            )

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return self.helper.populator_for_relativity_option_root(contents)

    def symbol_usage_expectation_assertions(self) -> list:
        return self.helper.symbol_usage_expectation_assertions()

    def symbol_entries_for_arrangement(self) -> list:
        return self.helper.symbol_entries_for_arrangement()

    def symbols_in_arrangement(self) -> SymbolTable:
        return self.helper.symbols_in_arrangement()


class RelativityOptionConfigurationForRelHome(RelativityOptionConfiguration):
    def __init__(self):
        super().__init__(file_ref_texts.REL_HOME_OPTION)

    @property
    def exists_pre_sds(self) -> bool:
        return True

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulatorForHomeContents:
        return HomeOrSdsPopulatorForHomeContents(contents)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(
            validation_pre_sds=svh_check.is_validation_error(),
            symbol_usages=self.symbol_usages_expectation(),
        )


class RelativityOptionConfigurationForRelSds(RelativityOptionConfiguration):
    @property
    def exists_pre_sds(self) -> bool:
        return False

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> sds_populator.SdsPopulator:
        raise NotImplementedError()

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForSdsContents(self.populator_for_relativity_option_root__sds(contents))

    def populator_for_relativity_option_root_for_contents_from_sds_fun(self,
                                                                       file_name: str,
                                                                       sds_2_file_contents_str
                                                                       ) -> SdsPopulator:
        return sds_populator.SdsPopulatorForFileWithContentsThatDependOnSds(
            file_name,
            sds_2_file_contents_str,
            self.populator_for_relativity_option_root__sds)

    def expectation_that_file_for_expected_contents_is_invalid(self) -> Expectation:
        return Expectation(
            main_result=pfh_check.is_fail(),
            symbol_usages=self.symbol_usages_expectation(),
        )


class RelativityOptionConfigurationForRelCwd(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(file_ref_texts.REL_CWD_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return pathlib.Path().cwd()

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return sds_populator.cwd_contents(contents)


class RelativityOptionConfigurationForRelAct(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(file_ref_texts.REL_ACT_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.act_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return sds_populator.act_dir_contents(contents)


class RelativityOptionConfigurationForRelTmp(RelativityOptionConfigurationForRelSds):
    def __init__(self):
        super().__init__(file_ref_texts.REL_TMP_OPTION)

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return sds.tmp.user_dir

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return sds_populator.tmp_user_dir_contents(contents)


class RelativityOptionConfigurationRelSdsForRelSymbol(RelativityOptionConfigurationForRelSds):
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str = 'SYMBOL_NAME'):
        super().__init__(rel_symbol_arg_str(symbol_name))
        self.helper = SymbolsRelativityHelper(relativity, expected_accepted_relativities, symbol_name)
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name
        if relativity is RelOptionType.REL_HOME:
            raise ValueError('Invalid relativity - must be rel SDS. Found: ' + str(relativity))

    def root_dir__sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        return REL_OPTIONS_MAP[self.relativity].root_resolver.from_sds(sds)

    def populator_for_relativity_option_root__sds(self, contents: DirContents) -> SdsPopulator:
        return sds_populator.rel_symbol(self.relativity, contents)

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return self.helper.populator_for_relativity_option_root(contents)

    def symbol_usage_expectation_assertions(self) -> list:
        return self.helper.symbol_usage_expectation_assertions()

    def symbol_entries_for_arrangement(self) -> list:
        return self.helper.symbol_entries_for_arrangement()

    def symbols_in_arrangement(self) -> SymbolTable:
        return self.helper.symbols_in_arrangement()


class _HomeOrSdsPopulatorForContentsThatDependOnHomeAndSds(HomeOrSdsPopulator):
    def __init__(self,
                 file_name: str,
                 home_and_sds_2_file_contents_str,
                 dir_contents__2_home_or_sds_populator):
        """
        :type home_and_sds_2_file_contents_str: `HomeAndAds` -> str
        :type dir_contents__2_home_or_sds_populator: `DirContents` -> `HomeOrSdsPopulator`
        """
        self.file_name = file_name
        self.home_and_sds_2_file_contents_str = home_and_sds_2_file_contents_str
        self.dir_contents__2_home_or_sds_populator = dir_contents__2_home_or_sds_populator

    def write_to(self, home_and_sds: HomeAndSds):
        file_contents = self.home_and_sds_2_file_contents_str(home_and_sds)
        dir_contents = DirContents([
            File(self.file_name, file_contents)
        ])
        home_or_sds_populator = self.dir_contents__2_home_or_sds_populator(dir_contents)
        home_or_sds_populator.write_to(home_and_sds)


class SymbolsRelativityHelper:
    def __init__(self,
                 relativity: RelOptionType,
                 expected_accepted_relativities: PathRelativityVariants,
                 symbol_name: str):
        self.expected_accepted_relativities = expected_accepted_relativities
        self.relativity = relativity
        self.symbol_name = symbol_name

    def populator_for_relativity_option_root(self, contents: DirContents) -> HomeOrSdsPopulator:
        return HomeOrSdsPopulatorForRelOptionType(self.relativity, contents)

    def symbol_usage_expectation(self) -> asrt.ValueAssertion:
        return asrt.matches_sequence(self.symbol_usage_expectation_assertions())

    def symbol_usage_expectation_assertions(self) -> list:
        return [
            equals_symbol_reference(
                self.symbol_name,
                equals_file_ref_relativity_restriction(
                    FileRefRelativityRestriction(self.expected_accepted_relativities)))

        ]

    def symbol_entries_for_arrangement(self) -> list:
        return [
            symbol_utils.entry(self.symbol_name,
                               FileRefConstant(file_refs.of_rel_option(self.relativity,
                                                                       PathPartAsNothing())))
        ]

    def symbols_in_arrangement(self) -> SymbolTable:
        return symbol_utils.symbol_table_from_entries(self.symbol_entries_for_arrangement())
