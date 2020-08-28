from typing import List, Sequence

from exactly_lib.actors import file_interpreter
from exactly_lib.actors import source_interpreter
from exactly_lib.actors.program import actor
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
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.actor import Actor
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.cli_syntax.option_parsing import matches
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
    def __init__(self, name: str,
                 single_line_description_un_formatted: str,
                 main_description_rest_un_formatted: str = None):
        self.single_line_description_un_formatted = single_line_description_un_formatted
        self.main_description_rest_un_formatted = main_description_rest_un_formatted
        super().__init__(name, {
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
            'act_phase': phase_names.ACT.emphasis,
            'command_line_actor': formatting.entity_(actors.COMMAND_LINE_ACTOR)
        })

    def single_line_description(self) -> str:
        return self._tp.format(self.single_line_description_un_formatted)

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
        if self.main_description_rest_un_formatted:
            return self._tp.fnap(self.main_description_rest_un_formatted)
        else:
            return []

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


def parse(instruction_argument: str) -> NameAndValue[Actor]:
    """
    :raises SingleInstructionInvalidArgumentException In case of invalid syntax
    """
    arg = instruction_argument.strip()
    if not arg:
        raise SingleInstructionInvalidArgumentException('An actor must be given')
    try:
        args = arg.split(maxsplit=2)
    except Exception as ex:
        raise SingleInstructionInvalidArgumentException(str(ex))
    if args[0] != instruction_arguments.ASSIGNMENT_OPERATOR:
        raise SingleInstructionInvalidArgumentException('Missing ' +
                                                        instruction_arguments.ASSIGNMENT_OPERATOR)
    del args[0]
    if not args:
        raise SingleInstructionInvalidArgumentException('Missing arguments after ' +
                                                        instruction_arguments.ASSIGNMENT_OPERATOR)
    if matches(COMMAND_LINE_ACTOR_OPTION_NAME, args[0]):
        if len(args) > 1:
            raise SingleInstructionInvalidArgumentException('Superfluous arguments to ' + args[0])
        return NameAndValue(actors.COMMAND_LINE_ACTOR.singular_name,
                            actor.actor())
    if len(args) == 1:
        raise SingleInstructionInvalidArgumentException('Missing file argument for ' + args[0])
    if matches(SOURCE_INTERPRETER_OPTION_NAME, args[0]):
        return NameAndValue(actors.SOURCE_INTERPRETER_ACTOR.singular_name,
                            _parse_source_interpreter(args[1]))
    if matches(FILE_INTERPRETER_OPTION_NAME, args[0]):
        return NameAndValue(actors.FILE_INTERPRETER_ACTOR.singular_name,
                            _parse_file_interpreter(args[1]))
    raise SingleInstructionInvalidArgumentException('Invalid option: "{}"'.format(args[0]))


def _parse_source_interpreter(arg: str) -> Actor:
    return source_interpreter.actor(parse_act_interpreter.parse(arg))


def _parse_file_interpreter(arg: str) -> Actor:
    return file_interpreter.actor(parse_act_interpreter.parse(arg))


_DESCRIPTION_OF_ACTOR_WITH_INTERPRETER = """\
Specifies that the {interpreter_actor} {actor} should be used, with the given interpreter.
"""

_DESCRIPTION_OF_COMMAND_LINE = """\
Specifies that the {command_line_actor} {actor} should be used.
"""
