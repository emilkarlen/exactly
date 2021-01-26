from typing import Sequence, List

from exactly_lib.impls.actors.util.actor_from_parts import parts
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.common import SymbolUser
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv


class InterpreterAndSourceInfo(SymbolUser):
    def __init__(self,
                 interpreter: CommandSdv,
                 source: StringSdv,
                 ):
        self.interpreter = interpreter
        self.source = source
        self._symbol_usages = tuple(interpreter.references) + tuple(source.references)

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._symbol_usages


class Parser(parts.ExecutableObjectParser[InterpreterAndSourceInfo]):
    def __init__(self, interpreter: CommandSdv):
        self._interpreter = interpreter

    def apply(self, instructions: Sequence[ActPhaseInstruction]) -> InterpreterAndSourceInfo:
        from exactly_lib.util.str_.misc_formatting import lines_content_with_os_linesep
        raw_source = lines_content_with_os_linesep(self._all_source_code_lines(instructions))
        source_sdv = parse_string.string_sdv_from_string(raw_source)
        return InterpreterAndSourceInfo(self._interpreter, source_sdv)

    @staticmethod
    def _all_source_code_lines(act_phase_instructions: Sequence[ActPhaseInstruction]) -> List[str]:
        ret_val = []
        for instruction in act_phase_instructions:
            for line in instruction.source_code().lines:
                ret_val.append(line)
        return ret_val
