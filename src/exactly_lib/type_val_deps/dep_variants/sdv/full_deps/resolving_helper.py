from typing import TypeVar

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsSdv
from exactly_lib.type_val_deps.types.files_condition.sdv import FilesConditionSdv, FilesCondition
from exactly_lib.type_val_deps.types.matcher import MODEL, MatcherSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib.type_val_prims.matcher.matching_result import MatchingResult
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class LogicTypeResolvingHelper:
    def __init__(self,
                 symbols: SymbolTable,
                 tcds: TestCaseDs,
                 application_environment: ApplicationEnvironment,
                 ):
        self._symbols = symbols
        self._tcds = tcds
        self._application_environment = application_environment

    @property
    def application_environment(self) -> ApplicationEnvironment:
        return self._application_environment

    @property
    def tcds(self) -> TestCaseDs:
        return self._tcds

    @property
    def symbols(self) -> SymbolTable:
        return self._symbols

    @property
    def file_space(self) -> DirFileSpace:
        return self.application_environment.tmp_files_space

    def resolve_full(self, sdv: FullDepsSdv[PRIMITIVE]) -> PRIMITIVE:
        return (
            sdv.resolve(self.symbols)
                .value_of_any_dependency(self.tcds)
                .primitive(self.application_environment)
        )

    def resolve_matcher(self, sdv: MatcherSdv[MODEL]) -> MatcherWTrace[MODEL]:
        return self.resolve_full(sdv)

    def resolve_program(self, sdv: ProgramSdv) -> Program:
        return self.resolve_full(sdv)

    def resolve_string_transformer(self, sdv: StringTransformerSdv) -> StringTransformer:
        return self.resolve_full(sdv)

    def resolve_program_command(self, sdv: ProgramSdv) -> Command:
        return self.resolve_full(sdv)

    def resolve_files_condition(self, sdv: FilesConditionSdv) -> FilesCondition:
        return self.resolve_full(sdv)

    def apply(self, sdv: MatcherSdv[MODEL], model: MODEL) -> MatchingResult:
        return self.resolve_matcher(sdv).matches_w_trace(model)


def resolving_helper__of_full_env(environment: FullResolvingEnvironment) -> LogicTypeResolvingHelper:
    return LogicTypeResolvingHelper(
        environment.symbols,
        environment.tcds,
        environment.application_environment,
    )
