from typing import Callable, List

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.instructions.assert_ import define_symbol as define_symbol__assert
from exactly_lib.instructions.before_assert import define_symbol as define_symbol__before_assert
from exactly_lib.instructions.cleanup import define_symbol as define_symbol__cleanup
from exactly_lib.instructions.setup import define_symbol as define_symbol__setup
from exactly_lib.processing.act_phase import ActPhaseSetup
from exactly_lib.processing.instruction_setup import InstructionsSetup
from exactly_lib.section_document import model
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.instruction_parsers import InstructionParserThatConsumesCurrentLine
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference, SymbolUsage
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.cli.program_modes.test_resources import main_program_execution
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import MainProgramConfig
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources import instruction_setup
from exactly_lib_test.execution.test_resources import instruction_test_resources as instrs
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActionToCheckExecutorParserThatRunsConstantActions
from exactly_lib_test.test_resources.actions import do_return

DEF_INSTRUCTION_NAME = 'define'
REF_INSTRUCTION_NAME = 'reference'


def define_string(symbol_name: str, value: str) -> str:
    return ' '.join([
        DEF_INSTRUCTION_NAME,
        types.STRING_TYPE_INFO.identifier,
        symbol_name,
        instruction_arguments.ASSIGNMENT_OPERATOR,
        value,
    ])


def reference_to(symbol_name: str,
                 value_type: ValueType) -> str:
    return ' '.join([
        REF_INSTRUCTION_NAME,
        ANY_TYPE_INFO_DICT[value_type].identifier,
        symbol_name,
    ])


TYPE_IDENT_2_VALUE_TYPE = {
    ANY_TYPE_INFO_DICT[value_type].identifier: value_type
    for value_type in ValueType
}


class _ReferenceParser(InstructionParserThatConsumesCurrentLine):
    def __init__(self, mk_instruction: Callable[[List[SymbolUsage]], model.Instruction]):
        self.mk_instruction = mk_instruction

    def _parse(self, rest_of_line: str) -> model.Instruction:
        parts = rest_of_line.split()
        if len(parts) != 2:
            raise SingleInstructionInvalidArgumentException('Usage TYPE NAME. Found: ' + rest_of_line)
        type_ident = parts[0]
        name = parts[1]

        try:
            reference = SymbolReference(name,
                                        ValueTypeRestriction(TYPE_IDENT_2_VALUE_TYPE[type_ident]))
            usages = [reference]
            return self.mk_instruction(usages)
        except KeyError:
            raise SingleInstructionInvalidArgumentException('Not a symbol type: ' + type_ident)


def _ref_instruction_setup(instruction_name: str,
                           mk_instruction: Callable[[List[SymbolUsage]], model.Instruction]
                           ) -> SingleInstructionSetup:
    return instruction_setup.single_instruction_setup_for_parser(instruction_name,
                                                                 _ReferenceParser(mk_instruction))


INSTRUCTION_SETUP = InstructionsSetup(
    setup_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__setup.setup(DEF_INSTRUCTION_NAME),
        REF_INSTRUCTION_NAME: _ref_instruction_setup(
            REF_INSTRUCTION_NAME,
            lambda usages: instrs.setup_phase_instruction_that(symbol_usages=do_return(usages))),
    },
    before_assert_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__before_assert.setup(DEF_INSTRUCTION_NAME),
        REF_INSTRUCTION_NAME: _ref_instruction_setup(
            REF_INSTRUCTION_NAME,
            lambda usages: instrs.before_assert_phase_instruction_that(symbol_usages=do_return(usages))),
    },
    assert_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__assert.setup(DEF_INSTRUCTION_NAME),
        REF_INSTRUCTION_NAME: _ref_instruction_setup(
            REF_INSTRUCTION_NAME,
            lambda usages: instrs.assert_phase_instruction_that(symbol_usages=do_return(usages))),
    },
    cleanup_instruction_set={
        DEF_INSTRUCTION_NAME: define_symbol__cleanup.setup(DEF_INSTRUCTION_NAME),
        REF_INSTRUCTION_NAME: _ref_instruction_setup(
            REF_INSTRUCTION_NAME,
            lambda usages: instrs.cleanup_phase_instruction_that(symbol_usages=do_return(usages))),
    },
)


def main_program_config() -> MainProgramConfig:
    return main_program_execution.main_program_config(test_case_definition_for(INSTRUCTION_SETUP),
                                                      act_phase_setup=act_phase_setup_for_reference_instruction())


def act_phase_setup_for_reference_instruction() -> ActPhaseSetup:
    return ActPhaseSetup(ActionToCheckExecutorParserThatRunsConstantActions())
