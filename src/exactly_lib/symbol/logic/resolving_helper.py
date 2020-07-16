from exactly_lib.symbol.logic.matcher import MODEL, MatcherSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDetailsDescriptionSdv, PRIMITIVE
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv, FilesCondition
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.files_matcher import FilesMatcher, FilesMatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


class LogicTypeResolvingHelper:
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: Tcds,
                 application_environment: ApplicationEnvironment,
                 ):
        self._symbols = symbols
        self._tcds = tcds
        self._application_environment = application_environment

    @property
    def application_environment(self) -> ApplicationEnvironment:
        return self._application_environment

    @property
    def tcds(self) -> Tcds:
        return self._tcds

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols

    @property
    def file_space(self) -> DirFileSpace:
        return self.application_environment.tmp_files_space

    def resolve_logic_w_describer(self, sdv: LogicWithDetailsDescriptionSdv[PRIMITIVE]) -> PRIMITIVE:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def resolve_matcher(self, sdv: MatcherSdv[MODEL]) -> MatcherWTrace[MODEL]:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def resolve_program(self, sdv: ProgramSdv) -> Program:
        return sdv.resolve(self.symbols).value_of_any_dependency(self.tcds).primitive(self.application_environment)

    def resolve_string_transformer(self, sdv: StringTransformerSdv) -> StringTransformer:
        return sdv.resolve(self.symbols).value_of_any_dependency(self.tcds).primitive(self.application_environment)

    def resolve_program_command(self, sdv: ProgramSdv) -> Command:
        return sdv.resolve(self.symbols).command.value_of_any_dependency(self.tcds)

    def resolve_files_condition(self, sdv: FilesConditionSdv) -> FilesCondition:
        return sdv.resolve(self.symbols).value_of_any_dependency(self.tcds).primitive(self.application_environment)

    def resolve_files_matcher(self, sdv: FilesMatcherSdv) -> FilesMatcher:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def apply(self, sdv: MatcherSdv[MODEL], model: MODEL) -> MatchingResult:
        return self.resolve_matcher(sdv).matches_w_trace(model)


def resolving_helper__of_full_env(environment: FullResolvingEnvironment) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
        environment.application_environment,
    )
