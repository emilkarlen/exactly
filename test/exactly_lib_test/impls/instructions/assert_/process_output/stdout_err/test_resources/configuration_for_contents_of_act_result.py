from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.file_contents.instruction_test_configuration import \
    InstructionTestConfiguration
from exactly_lib_test.tcfs.test_resources import tcds_populators as tcds
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducer, ActResultProducerFromActResult
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import TcdsAction
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx


class TestConfigurationForStdFile(InstructionTestConfiguration):
    def syntax_for_matcher(self, matcher: StringMatcherAbsStx) -> AbstractSyntax:
        return matcher

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: TcdsAction = TcdsAction(),
                                 tcds_contents: tcds.TcdsPopulator = tcds.empty(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        return instruction_check.ArrangementPostAct(
            act_result_producer=self._act_result_producer(actual_contents),
            tcds_contents=tcds_contents,
            post_sds_population_action=post_sds_population_action,
            symbols=symbols,
        )

    def act_result(self, contents_of_tested_file: str) -> SubProcessResult:
        raise NotImplementedError()

    def _act_result_producer(self, contents_of_tested_file: str) -> ActResultProducer:
        act_result = self.act_result(contents_of_tested_file)
        return ActResultProducerFromActResult(act_result)
