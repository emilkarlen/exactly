from exactly_lib.impls.actors.source_interpreter import parser as pa
from exactly_lib.impls.actors.source_interpreter.executor import Executor
from exactly_lib.impls.actors.util.actor_from_parts import parts
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.actor import Actor
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validators
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.sdv import sdv_validation
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
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

        return parts.ValidatorWithHardErrorFromPostSdsValidation(
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
