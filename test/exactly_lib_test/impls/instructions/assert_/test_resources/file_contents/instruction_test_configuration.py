from abc import abstractmethod, ABC

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__multi_line
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.tcfs.test_resources import tcds_populators as tcds
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.arguments.arguments_building import Arguments
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class InstructionTestConfiguration(ABC):
    def new_parser(self) -> InstructionParser:
        raise NotImplementedError()

    @property
    def checker(self) -> instruction_check.Checker:
        return instruction_check.Checker(self.new_parser())

    @property
    def parse_checker(self) -> parse_checker.Checker:
        return parse_checker.Checker(self.new_parser())

    @abstractmethod
    def syntax_for_matcher(self, matcher: AbstractSyntax) -> AbstractSyntax:
        raise NotImplementedError('abstract method')

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: TcdsAction = TcdsAction(),
                                 tcds_contents: tcds.TcdsPopulator = tcds.empty(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: InstructionTestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _check_with_source_variants(self,
                                    instruction_argument: Arguments,
                                    arrangement: ArrangementPostAct,
                                    expectation: Expectation):
        for source in equivalent_source_variants__with_source_check__multi_line(self, instruction_argument):
            instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)
