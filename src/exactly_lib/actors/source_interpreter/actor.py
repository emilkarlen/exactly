from exactly_lib.actors.source_interpreter import parser as pa
from exactly_lib.actors.source_interpreter.executor import Executor
from exactly_lib.actors.util.actor_from_parts import parts
from exactly_lib.symbol import sdv_validation
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case.actor import Actor
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case_file_structure import ddv_validators
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.util.symbol_table import SymbolTable

_ACT_SOURCE_FILE_BASE_NAME = 'act.src'


def actor(interpreter: CommandSdv) -> Actor:
    return parts.ActorFromParts(
        pa.Parser(interpreter),
        _TheValidatorConstructor(),
        _ExecutorConstructor(),
    )


class _TheValidatorConstructor(parts.ValidatorConstructor[pa.InterpreterAndSourceInfo]):
    def construct(self,
                  environment: InstructionEnvironmentForPreSdsStep,
                  executable_object: pa.InterpreterAndSourceInfo,
                  ) -> parts.Validator:
        def get_validator(symbols: SymbolTable) -> DdvValidator:
            return ddv_validators.all_of(executable_object.interpreter.resolve(symbols).validators)

        return parts.ValidatorFromPreOrPostSdsValidator(
            sdv_validation.SdvValidatorFromDdvValidator(get_validator)
        )


class _ExecutorConstructor(parts.ExecutorConstructor[pa.InterpreterAndSourceInfo]):
    def construct(self,
                  environment: InstructionEnvironmentForPostSdsStep,
                  os_services: OsServices,
                  object_to_execute: pa.InterpreterAndSourceInfo,
                  ) -> parts.Executor:
        return Executor(
            os_services,
            object_to_execute,
            _ACT_SOURCE_FILE_BASE_NAME,
        )