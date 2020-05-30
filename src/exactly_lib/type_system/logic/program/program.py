from typing import Sequence

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment, \
    LogicWithNodeDescriptionDdv
from exactly_lib.type_system.logic.program.command import CommandDdv
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv, StdinData
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerAdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node


class Program(WithCachedTreeStructureDescriptionBase):
    def __init__(self,
                 command: Command,
                 stdin: StdinData,
                 transformation: StringTransformer,
                 ):
        super().__init__()
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def _structure(self) -> StructureRenderer:
        return _StructureRendererOfPrimitive(self._command,
                                             self._transformation)

    @property
    def command(self) -> Command:
        return self._command

    @property
    def stdin(self) -> StdinData:
        return self._stdin

    @property
    def transformation(self) -> StringTransformer:
        return self._transformation


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

    def value_of_any_dependency(self, tcds: Tcds) -> ProgramAdv:
        return ProgramAdv(self.command.value_of_any_dependency(tcds),
                          self.stdin.value_of_any_dependency(tcds),
                          self.transformation.value_of_any_dependency(tcds))


class _StructureRendererOfDdv(NodeRenderer[None]):
    NAME = ' '.join((string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION,
                     syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT.singular_name))

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
            self.NAME,
            None,
            (),
            (self._transformation.structure(),),
        )


class _StructureRendererOfPrimitive(NodeRenderer[None]):

    def __init__(self,
                 command: Command,
                 transformation: StringTransformer,
                 ):
        self._command = command
        self._transformation = transformation

    def render(self) -> Node[None]:
        ret_val = self._command.structure()
        if not self._transformation.is_identity_transformer:
            ret_val.append_child(self._transformation_node())

        return ret_val.as_render().render()

    def _transformation_node(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            _StructureRendererOfDdv.NAME,
            None,
            (),
            (self._transformation.structure(),),
        )
