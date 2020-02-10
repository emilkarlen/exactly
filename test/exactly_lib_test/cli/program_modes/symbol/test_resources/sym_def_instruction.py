import itertools
from typing import Callable, List, Sequence, Optional

from exactly_lib.cli.main_program import BuiltinSymbol
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
from exactly_lib.symbol.sdv_structure import SymbolDependentValue, SymbolUsage, SymbolReference
from exactly_lib.test_case.actor import Actor, ActionToCheck, ParseException
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.result import svh, sh
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util import strings
from exactly_lib.util.textformat.structure import document
from exactly_lib_test.cli.program_modes.test_resources import main_program_execution
from exactly_lib_test.cli.program_modes.test_resources.main_program_execution import MainProgramConfig
from exactly_lib_test.cli.program_modes.test_resources.test_case_setup import test_case_definition_for
from exactly_lib_test.common.test_resources import instruction_documentation
from exactly_lib_test.common.test_resources import instruction_setup
from exactly_lib_test.common.test_resources.text_doc_assertions import new_pre_formatted_str_for_test
from exactly_lib_test.execution.test_resources import instruction_test_resources as instrs
from exactly_lib_test.execution.test_resources.instruction_test_resources import configuration_phase_instruction_that
from exactly_lib_test.test_case.actor.test_resources.action_to_checks import \
    ActionToCheckThatRunsConstantActions
from exactly_lib_test.test_case.actor.test_resources.actor_impls import ActorThatRunsConstantActions
from exactly_lib_test.test_resources.actions import do_return

DEF_INSTRUCTION_NAME = 'define'
REF_INSTRUCTION_NAME = 'reference'
SET_ACTOR_THAT_PARSES_REFERENCES_INSTRUCTION_NAME = 'set-source-interpreter-actor'
UNCONDITIONALLY_HARD_ERROR_CONF_PHASE_INSTRUCTION_NAME = 'unconditionally-hard-error'


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
        usages = _parse_reference_arguments(rest_of_line)
        return self.mk_instruction(usages)


def _parse_reference_arguments(rest_of_line: str) -> List[SymbolReference]:
    parts = rest_of_line.split()
    if len(parts) != 2:
        raise SingleInstructionInvalidArgumentException('Usage TYPE NAME. Found: ' + rest_of_line)
    type_ident = parts[0]
    name = parts[1]

    try:
        reference = SymbolReference(name,
                                    ValueTypeRestriction(TYPE_IDENT_2_VALUE_TYPE[type_ident]))
        return [reference]
    except KeyError:
        raise SingleInstructionInvalidArgumentException('Not a symbol type: ' + type_ident)


def _ref_instruction_setup(instruction_name: str,
                           mk_instruction: Callable[[List[SymbolUsage]], model.Instruction]
                           ) -> SingleInstructionSetup:
    return instruction_setup.single_instruction_setup_for_parser(instruction_name,
                                                                 _ReferenceParser(mk_instruction))


def _setup_for_actor_that_parses_references(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        _SetActorThatParsesReferences(),
        instruction_documentation.instruction_documentation(instruction_name),
    )


def _setup_hard_error_conf_phase_instruction(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        _ParserOfConfPhaseInstructionThatCausesHardError(),
        instruction_documentation.instruction_documentation(instruction_name),
    )


class _SetActorThatParsesReferences(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> model.Instruction:
        return _InstructionThatSetsInterpreterActor()


class _ParserOfConfPhaseInstructionThatCausesHardError(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> model.Instruction:
        return configuration_phase_instruction_that(
            main=do_return(sh.new_sh_hard_error__str('unconditional hard error'))
        )


class _InstructionThatSetsInterpreterActor(ConfigurationPhaseInstruction):
    def main(self, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_actor(_ActorThatParsesReferences(REF_INSTRUCTION_NAME))
        return sh.new_sh_success()


INSTRUCTION_SETUP = InstructionsSetup(
    config_instruction_set={
        SET_ACTOR_THAT_PARSES_REFERENCES_INSTRUCTION_NAME:
            _setup_for_actor_that_parses_references(SET_ACTOR_THAT_PARSES_REFERENCES_INSTRUCTION_NAME),

        UNCONDITIONALLY_HARD_ERROR_CONF_PHASE_INSTRUCTION_NAME:
            _setup_hard_error_conf_phase_instruction(UNCONDITIONALLY_HARD_ERROR_CONF_PHASE_INSTRUCTION_NAME),
    },
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


def main_program_config(actor: Optional[Actor] = None,
                        builtin_symbols: Sequence[BuiltinSymbol] = (),
                        ) -> MainProgramConfig:
    if actor is None:
        actor = _ActorThatParsesReferences(REF_INSTRUCTION_NAME)
    return main_program_execution.main_program_config(
        test_case_definition_for(INSTRUCTION_SETUP, builtin_symbols),
        act_phase_setup=ActPhaseSetup(
            actor
        )
    )


def act_phase_setup_for_reference_instruction() -> ActPhaseSetup:
    return ActPhaseSetup(ActorThatRunsConstantActions())


class _ActorThatParsesReferences(Actor):
    def __init__(self, reference_instruction_name: str):
        self._reference_instruction_name = reference_instruction_name

    def parse(self, instructions: Sequence[ActPhaseInstruction]) -> ActionToCheck:
        try:
            source_lines = list(itertools.chain.from_iterable(map(self._get_source_code_lines, instructions)))
            reference_instructions_arguments = self._get_reference_instruction_arguments(source_lines)
            references = list(
                itertools.chain.from_iterable(map(_parse_reference_arguments, reference_instructions_arguments)))

            return ActionToCheckThatRunsConstantActions(
                symbol_usages_action=do_return(references)
            )
        except SingleInstructionInvalidArgumentException as ex:
            raise ParseException(svh.new_svh_validation_error__str(ex.error_message))

    def _get_reference_instruction_arguments(self, lines: Sequence[str]) -> List[str]:
        ret_val = []
        for line in lines:
            if not line or line.isspace():
                continue
            parts = line.split(maxsplit=1)
            if len(parts) == 2 and parts[0] == self._reference_instruction_name:
                ret_val.append(parts[1])
            else:
                err_msg = new_pre_formatted_str_for_test(
                    strings.FormatPositional(
                        'Invalid act phase instruction: {}\nExpecting: {}',
                        line,
                        self._reference_instruction_name)
                )
                raise ParseException(svh.new_svh_validation_error(err_msg))

        return ret_val

    @staticmethod
    def _get_source_code_lines(instruction: ActPhaseInstruction) -> Sequence[str]:
        return instruction.source_code().lines


def builtin_symbol(name: str,
                   sdv: SymbolDependentValue) -> BuiltinSymbol:
    return BuiltinSymbol(
        name,
        sdv,
        'the single line description',
        document.empty_section_contents(),
    )
