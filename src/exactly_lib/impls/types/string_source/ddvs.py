from typing import Sequence

from exactly_lib.impls import file_properties
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.path import path_check
from exactly_lib.impls.types.utils.command_w_stdin import CommandWStdin
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import PRIMITIVE
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.program.ddv.command import CommandDdv
from exactly_lib.type_val_deps.types.string_.string_ddv import StringDdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.program import program
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from . import constant_str, file_source
from .command_output import string_source as cmd_string_source
from ...file_properties import FileType


class ConstantStringStringSourceDdv(StringSourceDdv):
    def __init__(self, string: StringDdv):
        self._string = string

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return constant_str.FactoryOfStringSourceStructureBuilder(self._string.describer()).new()

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringSource:
            return constant_str.string_source(
                self._string.value_of_any_dependency(tcds),
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)


class PathStringSourceDdv(StringSourceDdv):
    def __init__(self, path: PathDdv):
        self._path = path
        self._validator = path_check.PathCheckDdvValidator(
            path_check.PathCheckDdv(
                path,
                file_properties.must_exist_as(FileType.REGULAR)
            )
        )

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return file_source.StringSourceOfFile.structure_builder_for(
            custom_details.PathDdvDetailsRenderer(self._path.describer())
        )

    @property
    def validator(self) -> DdvValidator:
        return self._validator

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringSource:
            return file_source.string_source_of_file__described(
                self._path.value_of_any_dependency__d(tcds),
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)


class CommandOutputStringSourceDdv(StringSourceDdv):
    def __init__(self,
                 structure_header: str,
                 ignore_exit_code: bool,
                 output_channel_to_capture: ProcOutputFile,
                 command: CommandDdv,
                 command_stdin: Sequence[StringSourceDdv],
                 ):
        self._structure_header = structure_header
        self._ignore_exit_code = ignore_exit_code
        self._output_channel_to_capture = output_channel_to_capture
        self._command = command
        self._command_stdin = command_stdin
        self._validators = (
                list(self._command.validators) +
                [
                    part.validator
                    for part in command_stdin
                ]
        )

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return cmd_string_source.ConstructorOfStructureBuilder(
            self._structure_header,
            self._ignore_exit_code,
            self._structure_of_command(),
        ).new_structure_builder()

    def _structure_of_command(self) -> StructureRenderer:
        return program.command_w_stdin_renderer(
            self._command.structure(),
            self._command_stdin,
        )

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of(self._validators)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringSource:
            command = self._command.value_of_any_dependency(tcds)
            command_stdin = [
                ss.value_of_any_dependency(tcds).primitive(environment)
                for ss in self._command_stdin
            ]
            return cmd_string_source.string_source(
                self._structure_header,
                self._ignore_exit_code,
                self._output_channel_to_capture,
                CommandWStdin(command, command_stdin),
                environment.process_execution_settings,
                environment.os_services.command_executor,
                environment.mem_buff_size,
                environment.tmp_files_space,
            )

        return advs.AdvFromFunction(make_primitive)


class TransformedStringSourceDdv(StringSourceDdv):
    def __init__(self,
                 transformed: StringSourceDdv,
                 transformer: StringTransformerDdv,
                 ):
        self._transformed = transformed
        self._transformer = transformer

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._transformer.structure())

    @property
    def validator(self) -> DdvValidator:
        return ddv_validators.all_of([self._transformed.validator,
                                      self._transformer.validator])

    def value_of_any_dependency(self, tcds: TestCaseDs) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        def make_primitive(environment: ApplicationEnvironment) -> StringSource:
            transformed = self._transformed.value_of_any_dependency(tcds).primitive(environment)
            transformer = self._transformer.value_of_any_dependency(tcds).primitive(environment)
            return transformer.transform(transformed)

        return advs.AdvFromFunction(make_primitive)
