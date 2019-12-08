from typing import Callable

from exactly_lib.instructions.assert_ import contents_of_file as sut
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.test_case.test_resources.arrangements import ActEnvironment, ActResultProducer
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators as home_or_sds, \
    sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.tcds_populators import \
    TcdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction


class TestConfigurationForFile(InstructionTestConfigurationForEquals):
    FILE_NAME_REL_ACT = 'actual.txt'
    FILE_NAME_REL_CWD = '../actual.txt'

    def new_parser(self) -> InstructionParser:
        return sut.parser('the-instruction-name')

    def arguments_for(self, additional_arguments: str) -> Arguments:
        return Arguments(self.FILE_NAME_REL_CWD + ' ' + additional_arguments)

    def arrangement_for_contents(self, actual_contents: str,
                                 post_sds_population_action: TcdsAction = TcdsAction(),
                                 home_or_sds_contents: home_or_sds.TcdsPopulator = home_or_sds.empty(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            tcds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arrangement_for_contents_from_fun(self,
                                          tcds_2_str: Callable[[Tcds], str],
                                          home_or_sds_contents: home_or_sds.TcdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: TcdsAction = TcdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> instruction_check.ArrangementPostAct:
        act_result_producer = _ActResultProducer(tcds_2_str, self.FILE_NAME_REL_ACT)
        return instruction_check.ArrangementPostAct(
            act_result_producer=act_result_producer,
            tcds_contents=home_or_sds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: TcdsPopulator,
                                            post_sds_population_action: TcdsAction = TcdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            sds_contents=self._populator_for_actual(actual_contents),
            tcds_contents=expected,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def _populator_for_actual(self, actual_contents) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                         DirContents([
                                             File(self.FILE_NAME_REL_ACT, actual_contents)
                                         ]))


class _ActResultProducer(ActResultProducer):
    def __init__(self,
                 tcds_2_str: Callable[[Tcds], str],
                 file_name: str):
        self.tcds_2_str = tcds_2_str
        self.file_name = file_name

    def apply(self, act_environment: ActEnvironment) -> SubProcessResult:
        self._populate_act_dir(act_environment)
        return SubProcessResult()

    def _populate_act_dir(self, act_environment: ActEnvironment):
        actual_contents = self.tcds_2_str(act_environment.tcds)
        sds_pop = sds_populator.contents_in(RelSdsOptionType.REL_ACT,
                                            DirContents([
                                                File(self.file_name, actual_contents)
                                            ]))
        sds_pop.populate_sds(act_environment.tcds.sds)
