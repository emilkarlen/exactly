from typing import Sequence

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithNodeDescriptionDdv
from exactly_lib.type_val_deps.types.program.ddv.command import CommandDdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv, StringSourceAdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program import program
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program


class ProgramAdv(ApplicationEnvironmentDependentValue[Program]):
    def __init__(self,
                 command: Command,
                 stdin: Sequence[StringSourceAdv],
                 transformation: Sequence[StringTransformerAdv],
                 ):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def primitive(self, environment: ApplicationEnvironment) -> Program:
        return Program(self._command,
                       [ss.primitive(environment) for ss in self._stdin],
                       [st.primitive(environment) for st in self._transformation],
                       )


class ProgramDdv(FullDepsWithNodeDescriptionDdv[Program]):
    def __init__(self,
                 command: CommandDdv,
                 stdin: Sequence[StringSourceDdv],
                 transformations: Sequence[StringTransformerDdv],
                 ):
        self._command = command
        self._stdin = stdin
        self._transformations = transformations
        self._validators = (
                list(command.validators)
                + [st.validator for st in transformations]
                + [ss.validator for ss in stdin]
        )

    @property
    def command(self) -> CommandDdv:
        return self._command

    @property
    def stdin(self) -> Sequence[StringSourceDdv]:
        return self._stdin

    @property
    def has_transformations(self) -> bool:
        return len(self._transformations) > 0

    @property
    def transformations(self) -> Sequence[StringTransformerDdv]:
        return self._transformations

    def structure(self) -> StructureRenderer:
        return program.program_structure_renderer(self._command.structure(),
                                                  self._stdin,
                                                  self._transformations)

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of(self._validators)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ProgramAdv:
        return ProgramAdv(
            self.command.value_of_any_dependency(tcds),
            [ss.value_of_any_dependency(tcds) for ss in self.stdin],
            [st.value_of_any_dependency(tcds) for st in self._transformations],
        )
