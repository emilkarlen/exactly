from typing import Sequence

from exactly_lib.tcfs import ddv_validators
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv.app_env_dep_ddv import LogicWithNodeDescriptionDdv
from exactly_lib.type_val_deps.types.program.ddv.command import CommandDdv
from exactly_lib.type_val_deps.types.program.ddv.stdin_data import StdinDataDdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerAdv, StringTransformerDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program import program
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.program.stdin import StdinData
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class ProgramAdv(ApplicationEnvironmentDependentValue[Program]):
    def __init__(self,
                 command: Command,
                 stdin: StdinData,
                 transformation: StringTransformerAdv):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def primitive(self, environment: ApplicationEnvironment) -> Program:
        return Program(self._command,
                       self._stdin,
                       self._transformation.primitive(environment),
                       )


class ProgramDdv(LogicWithNodeDescriptionDdv[Program]):
    def __init__(self,
                 command: CommandDdv,
                 stdin: StdinDataDdv,
                 transformation: StringTransformerDdv,
                 has_transformations: bool):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation
        self._validators = (tuple(command.validators) + (transformation.validator,))
        self._has_transformations = has_transformations

    @property
    def command(self) -> CommandDdv:
        return self._command

    @property
    def stdin(self) -> StdinDataDdv:
        return self._stdin

    @property
    def transformation(self) -> StringTransformerDdv:
        return self._transformation

    def structure(self) -> StructureRenderer:
        return _StructureRendererOfDdv(self._command,
                                       self._transformation,
                                       self._has_transformations)

    @property
    def validators(self) -> Sequence[DdvValidator]:
        return self._validators

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of(self._validators)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ProgramAdv:
        return ProgramAdv(self.command.value_of_any_dependency(tcds),
                          self.stdin.value_of_any_dependency(tcds),
                          self.transformation.value_of_any_dependency(tcds))


class _StructureRendererOfDdv(NodeRenderer[None]):
    def __init__(self,
                 command: CommandDdv,
                 transformation: StringTransformerDdv,
                 has_transformations: bool,
                 ):
        self._command = command
        self._transformation = transformation
        self._has_transformations = has_transformations

    def render(self) -> Node[None]:
        ret_val = self._command.structure()
        if self._has_transformations:
            ret_val.append_child(self._transformation_node())

        return ret_val.as_render().render()

    def _transformation_node(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            program.NAME,
            None,
            (),
            (self._transformation.structure(),),
        )
