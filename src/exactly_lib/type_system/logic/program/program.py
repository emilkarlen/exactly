from typing import Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case.validation import ddv_validators
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription, StructureRenderer
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, ApplicationEnvironment
from exactly_lib.type_system.logic.program.command import CommandDdv
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv, StdinData
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerAdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.process_execution.command import Command


class Program(tuple):
    def __new__(cls,
                command: Command,
                stdin: StdinData,
                transformation: StringTransformer):
        return tuple.__new__(cls, (command, stdin, transformation))

    @property
    def command(self) -> Command:
        return self[0]

    @property
    def stdin(self) -> StdinData:
        return self[1]

    @property
    def transformation(self) -> StringTransformer:
        return self[2]


class ProgramAdv(ApplicationEnvironmentDependentValue[Program]):
    def __init__(self,
                 command: Command,
                 stdin: StdinData,
                 transformation: StringTransformerAdv):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation

    def applier(self, environment: ApplicationEnvironment) -> Program:
        return Program(self._command,
                       self._stdin,
                       self._transformation.applier(environment),
                       )


class ProgramDdv(DirDependentValue[ApplicationEnvironmentDependentValue[Program]],
                 WithTreeStructureDescription):
    def __init__(self,
                 command: CommandDdv,
                 stdin: StdinDataDdv,
                 transformation: StringTransformerDdv,
                 has_transformations: bool):
        self._command = command
        self._stdin = stdin
        self._transformation = transformation
        self._validators = (tuple(command.validators) + (transformation.validator(),))
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
        return _StructureRenderer(self._command,
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


class _StructureRenderer(NodeRenderer[None]):
    _NAME = ' '.join((instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION,
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
            self._NAME,
            None,
            (),
            (self._transformation.structure(),),
        )
