from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.file_contents.equals import \
    InstructionTestConfigurationForEquals
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducer, ActResultProducerFromActResult
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomeOrSdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import HomeAndSdsAction


class TestConfigurationForStdFile(InstructionTestConfigurationForEquals):
    def arguments_for(self, additional_arguments: str) -> Arguments:
        return Arguments(additional_arguments)

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def arrangement_for_actual_and_expected(self,
                                            actual_contents: str,
                                            expected: HomeOrSdsPopulator,
                                            post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                            symbols: SymbolTable = None,
                                            ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=(self._act_result_producer(actual_contents)),
            home_or_sds_contents=expected,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def act_result(self, contents_of_tested_file: str) -> SubProcessResult:
        raise NotImplementedError()

    def _act_result_producer(self, contents_of_tested_file: str) -> ActResultProducer:
        act_result = self.act_result(contents_of_tested_file)
        return ActResultProducerFromActResult(act_result)
