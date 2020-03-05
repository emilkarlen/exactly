from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.matcher import MODEL, MatcherSdv, MatcherTypeStv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.resolving_environment import FullResolvingEnvironment
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.described_dep_val import LogicWithDescriberSdv, PRIMITIVE
from exactly_lib.type_system.logic.files_matcher import FilesMatcher, FilesMatcherModel
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.program import Program
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.symbol_table import SymbolTable


class LogicTypeResolvingHelper:
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: Tcds,
                 file_space: TmpDirFileSpace,
                 ):
        self._symbols = symbols
        self._tcds = tcds
        self._file_space = file_space
        self._application_environment = ApplicationEnvironment(file_space)

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
    def file_space(self) -> TmpDirFileSpace:
        return self.application_environment.tmp_files_space

    def resolve_generic_sdv(self, sdv: LogicWithDescriberSdv[PRIMITIVE]) -> PRIMITIVE:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def resolve(self, sdv: MatcherTypeStv[MODEL]) -> MatcherWTraceAndNegation[MODEL]:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def resolve__generic(self, sdv: MatcherSdv[MODEL]) -> MatcherWTraceAndNegation[MODEL]:
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

    def resolve_files_matcher(self, sdv: FilesMatcherStv) -> FilesMatcher:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def apply(self, sdv: MatcherTypeStv[MODEL], model: MODEL) -> MatchingResult:
        return self.resolve(sdv).matches_w_trace(model)

    def apply__generic(self, sdv: MatcherSdv[MODEL], model: MODEL) -> MatchingResult:
        return self.resolve__generic(sdv).matches_w_trace(model)

    def apply__files_matcher(self, sdv: FilesMatcherStv, model: FilesMatcherModel) -> MatchingResult:
        return self.resolve_files_matcher(sdv).matches_w_trace(model)


def resolving_helper__of_full_env(environment: FullResolvingEnvironment) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
        environment.application_environment.tmp_files_space,
    )
