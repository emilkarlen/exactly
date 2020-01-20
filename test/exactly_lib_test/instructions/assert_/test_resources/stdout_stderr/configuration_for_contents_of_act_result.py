from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer, ActResultProducerFromActResult
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators as home_or_sds
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import TcdsAction


class TestConfigurationForStdFile(InstructionTestConfigurationForEquals):
    def arguments_for(self, additional_arguments: str) -> Arguments:
        return Arguments(additional_arguments)

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: TcdsAction = TcdsAction(),
                                 tcds_contents: home_or_sds.TcdsPopulator = home_or_sds.empty(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=self._act_result_producer(actual_contents),
            tcds_contents=tcds_contents,
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
            act_result_producer=(self._act_result_producer(actual_contents)),
            tcds_contents=expected,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def act_result(self, contents_of_tested_file: str) -> SubProcessResult:
        raise NotImplementedError()

    def _act_result_producer(self, contents_of_tested_file: str) -> ActResultProducer:
        act_result = self.act_result(contents_of_tested_file)
        return ActResultProducerFromActResult(act_result)
