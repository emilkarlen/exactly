from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.impls.instructions.multi_phase.environ import defs
from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.types.string_source.test_resources.abstract_syntaxes import StringSourceOfStringAbsStx
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.source.token_sequences import OptionWMandatoryValue
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntax import NonHereDocStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx
from exactly_lib_test.util.test_resources.quoting import Surrounded

_PHASE_SPEC_VALUES = {
    Phase.ACT: defs.PHASE_SPEC__ACT,
    Phase.NON_ACT: defs.PHASE_SPEC__NON_ACT,
}


class InstructionArgumentsAbsStx(AbstractSyntax, ABC):
    def __init__(self, phase_spec: Optional[Phase]):
        self.phase_spec = phase_spec

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._phase_spec_tokenization(),
            self._variant_tokenization(),
        ])

    @abstractmethod
    def _variant_tokenization(self) -> TokenSequence:
        pass

    def _phase_spec_tokenization(self) -> TokenSequence:
        return (
            TokenSequence.empty()
            if self.phase_spec is None
            else
            OptionWMandatoryValue.of_option_name__str_arg(
                defs.PHASE_SPEC__OPTION_NAME,
                _PHASE_SPEC_VALUES[self.phase_spec],
            )
        )


class SetVariableArgumentsAbsStx(InstructionArgumentsAbsStx):
    def __init__(self,
                 var_name: NonHereDocStringAbsStx,
                 value: StringSourceAbsStx,
                 phase_spec: Optional[Phase],
                 ):
        super().__init__(phase_spec)
        self.var_name = var_name
        self.value = value

    @staticmethod
    def of_str(var_name: str,
               value: str,
               phase_spec: Optional[Phase],
               quoting: Optional[QuoteType] = None,
               ) -> 'SetVariableArgumentsAbsStx':
        return SetVariableArgumentsAbsStx(StringLiteralAbsStx(var_name),
                                          StringSourceOfStringAbsStx.of_str(value, quoting),
                                          phase_spec)

    @staticmethod
    def of_nav(var_and_val: NameAndValue[str],
               phase_spec: Optional[Phase]) -> 'SetVariableArgumentsAbsStx':
        return SetVariableArgumentsAbsStx.of_str(var_and_val.name,
                                                 var_and_val.value,
                                                 phase_spec=phase_spec)

    def _variant_tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self.var_name.tokenization(),
            TokenSequence.optional_new_line(),
            TokenSequence.singleton(defs.ASSIGNMENT_IDENTIFIER),
            TokenSequence.optional_new_line(),
            self.value.tokenization(),
        ])


class UnsetVariableArgumentsAbsStx(InstructionArgumentsAbsStx):
    def __init__(self,
                 var_name: NonHereDocStringAbsStx,
                 phase_spec: Optional[Phase],
                 ):
        super().__init__(phase_spec)
        self.var_name = var_name

    @staticmethod
    def of_str(var_name: str,
               phase_spec: Optional[Phase],
               quoting: Optional[QuoteType] = None,
               ) -> 'UnsetVariableArgumentsAbsStx':
        return UnsetVariableArgumentsAbsStx(StringLiteralAbsStx(var_name, quoting),
                                            phase_spec)

    def _variant_tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(defs.UNSET_IDENTIFIER),
            TokenSequence.optional_new_line(),
            self.var_name.tokenization(),
        ])


def env_var_ref_syntax(var_name: str) -> str:
    return str(Surrounded('${', '}', var_name))


def end_of_1st_var_ref(expr: str) -> int:
    return expr.find('}')
