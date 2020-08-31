from typing import List, Sequence, Dict, Callable

from exactly_lib.actors import file_interpreter
from exactly_lib.actors.program import actor as program_actor
from exactly_lib.actors.source_interpreter import actor
from exactly_lib.actors.util import parse_act_interpreter
from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions import formatting, instruction_arguments
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts, actors, syntax_elements
from exactly_lib.definitions.entity.actors import FILE_INTERPRETER_ACTOR
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.instructions.configuration.utils.single_arg_utils import MANDATORY_EQ_ARG
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.actor import Actor
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_syntax import long_option_syntax
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.textformat.structure.core import ParagraphItem

COMMAND_LINE_ACTOR_OPTION_NAME = a.OptionName(long_name='command')
COMMAND_LINE_ACTOR_OPTION = long_option_syntax(COMMAND_LINE_ACTOR_OPTION_NAME.long)

SOURCE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='source')
SOURCE_INTERPRETER_OPTION = long_option_syntax(SOURCE_INTERPRETER_OPTION_NAME.long)

FILE_INTERPRETER_OPTION_NAME = a.OptionName(long_name='file')
FILE_INTERPRETER_OPTION = long_option_syntax(FILE_INTERPRETER_OPTION_NAME.long)


class InstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': phase_names.ACT.emphasis,
            'command_line_actor': formatting.entity_(actors.COMMAND_LINE_ACTOR),
            'ACT_INTERPRETER': syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.singular_name,
            'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
            'setup': phase_names.SETUP,
        })

    def single_line_description(self) -> str:
        return self._tp.format(_SINGLE_LINE_DESCRIPTION)

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        from exactly_lib.definitions.entity.actors import SOURCE_INTERPRETER_ACTOR
        source_interpreter_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(SOURCE_INTERPRETER_OPTION_NAME))
        file_interpreter_arg = a.Single(a.Multiplicity.MANDATORY, a.Option(FILE_INTERPRETER_OPTION_NAME))
        return (
            self._command_line_invokation_variant(),
            self._interpreter_actor_invokation_variant(FILE_INTERPRETER_ACTOR,
                                                       file_interpreter_arg),
            self._interpreter_actor_invokation_variant(SOURCE_INTERPRETER_ACTOR,
                                                       source_interpreter_arg),
        )

    def main_description_rest(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        from exactly_lib.definitions.entity.actors import all_actor_cross_refs
        return ([concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
                 syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.cross_reference_target,
                 ]
                +
                all_actor_cross_refs()
                )

    def _command_line_invokation_variant(self) -> InvokationVariant:
        command_line_actor_arg = a.Single(a.Multiplicity.MANDATORY,
                                          a.Option(COMMAND_LINE_ACTOR_OPTION_NAME))
        return invokation_variant_from_args([MANDATORY_EQ_ARG, command_line_actor_arg],
                                            self._description_of_command_line()
                                            )

    def _interpreter_actor_invokation_variant(self,
                                              actor_w_interpreter: SingularNameAndCrossReferenceId,
                                              cli_option: a.Single) -> InvokationVariant:
        return invokation_variant_from_args([MANDATORY_EQ_ARG,
                                             cli_option,
                                             syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT.single_mandatory,
                                             ],
                                            self._description_of_actor_with_interpreter(actor_w_interpreter))

    def _description_of_actor_with_interpreter(self,
                                               actor_w_interpreter: SingularNameAndCrossReferenceId,
                                               ) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_ACTOR_WITH_INTERPRETER, {
            'interpreter_actor': formatting.entity(actor_w_interpreter.singular_name)
        })

    def _description_of_command_line(self) -> List[ParagraphItem]:
        return self._tp.fnap(_DESCRIPTION_OF_COMMAND_LINE)


def parse(source: ParseSource) -> NameAndValue[Actor]:
    with token_stream_parser.from_parse_source(source,
                                               consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
        return _parse_from_token_parser(token_parser)


def _parse_from_token_parser(token_parser: TokenParser) -> NameAndValue[Actor]:
    token_parser.consume_mandatory_keyword(instruction_arguments.ASSIGNMENT_OPERATOR, False)
    ret_val = token_parser.parse_mandatory_command(_actor_parsers_setup(),
                                                   concepts.ACTOR_CONCEPT_INFO.singular_name.upper())
    token_parser.report_superfluous_arguments_if_not_at_eol()
    return ret_val


def _actor_parsers_setup() -> Dict[str, Callable[[TokenParser], NameAndValue[Actor]]]:
    return {
        COMMAND_LINE_ACTOR_OPTION: _parse_command_line_actor,

        FILE_INTERPRETER_OPTION: _parse_file_actor,

        SOURCE_INTERPRETER_OPTION: _parse_source_actor,
    }


def _parse_command_line_actor(token_parser: TokenParser) -> NameAndValue[Actor]:
    return NameAndValue(actors.COMMAND_LINE_ACTOR.singular_name,
                        program_actor.actor())


def _parse_file_actor(token_parser: TokenParser) -> NameAndValue[Actor]:
    act_interpreter = parse_act_interpreter.parser().parse_from_token_parser(token_parser)
    return NameAndValue(actors.FILE_INTERPRETER_ACTOR.singular_name,
                        file_interpreter.actor(act_interpreter))


def _parse_source_actor(token_parser: TokenParser) -> NameAndValue[Actor]:
    act_interpreter = parse_act_interpreter.parser().parse_from_token_parser(token_parser)
    return NameAndValue(actors.SOURCE_INTERPRETER_ACTOR.singular_name,
                        actor.actor(act_interpreter))


_SINGLE_LINE_DESCRIPTION = 'Specifies the {actor} that will execute the {act_phase} phase'

_MAIN_DESCRIPTION_REST = """\
The {actor} specified by this instruction has precedence over all other ways
to specify the actor.


{ACT_INTERPRETER} may reference {symbol:s} defined in the {setup:emphasis} phase.
"""

_DESCRIPTION_OF_ACTOR_WITH_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with the given interpreter.
"""

_DESCRIPTION_OF_COMMAND_LINE = """\
Specifies that the {command_line_actor} {actor} should be used.
"""
