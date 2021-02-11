from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments, formatting, misc_texts
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts, actors
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.impls.types.string_source import parse as parse_str_src
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self._tp = TextParser({
            'stdin': misc_texts.STDIN,
            'atc': formatting.concept(concepts.ACTION_TO_CHECK_NAME.singular),
            'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
            'run_program_actor': formatting.entity_(actors.COMMAND_LINE_ACTOR),
            'actor': formatting.concept_(concepts.ACTOR_CONCEPT_INFO),
        })

    def single_line_description(self) -> str:
        return self._tp.format('Sets the contents of {stdin} for the {atc}')

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, a.Constant(instruction_arguments.ASSIGNMENT_OPERATOR)),
                syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.single_mandatory,
            ]),
        ]

    def notes(self) -> SectionContents:
        return self._tp.section_contents(_NOTES)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return cross_reference_id_list([
            phase_infos.ACT,
            concepts.ACTION_TO_CHECK_CONCEPT_INFO,
            actors.COMMAND_LINE_ACTOR,
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
        ])


class Parser(InstructionParserWithoutSourceFileLocationInfo):
    def __init__(self):
        self._str_src_parser = parse_str_src.default_parser_for(phase_is_after_act=False,
                                                                default_relativity=RelOptionType.REL_HDS_CASE)

    def parse_from_source(self, source: ParseSource) -> SetupPhaseInstruction:
        with from_parse_source(source, consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            token_parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
                [instruction_arguments.ASSIGNMENT_OPERATOR],
                lambda x: x
            )
            string_source = self._str_src_parser.parse_from_token_parser(token_parser)

            token_parser.report_superfluous_arguments_if_not_at_eol()
            token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

            return _Instruction(string_source)


class _Instruction(SetupPhaseInstruction):
    def __init__(self, contents: StringSourceSdv):
        self._contents = contents

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self._contents.references

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep,
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        ddv = self._contents.resolve(environment.symbols)
        return svh.new_maybe_svh_validation_error(
            ddv.validator.validate_pre_sds_if_applicable(environment.hds)
        )

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             settings: InstructionSettings,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder,
             ) -> sh.SuccessOrHardError:
        settings_builder.stdin = _StdinOfStringSource(
            self._contents.resolve(environment.symbols),
            environment.tcds,
        )
        return sh.new_sh_success()


class _StdinOfStringSource(AdvWValidation[StringSource]):
    def __init__(self,
                 string_source: StringSourceDdv,
                 tcds: TestCaseDs,
                 ):
        self._string_source = string_source
        self._tcds = tcds

    def validate(self) -> Optional[TextRenderer]:
        mb_str_src_err_msg_renderer = self._string_source.validator.validate_post_sds_if_applicable(self._tcds)
        return (
            None
            if mb_str_src_err_msg_renderer is None
            else
            rend_comb.ConcatenationR([
                text_docs.single_line(_STDIN_VALIDATION_ERROR_HEADER),
                rend_comb.Indented(mb_str_src_err_msg_renderer),
            ]
            )
        )

    def resolve(self, environment: ApplicationEnvironment) -> StringSource:
        return self._string_source.value_of_any_dependency(self._tcds).primitive(environment)


_STDIN_VALIDATION_ERROR_HEADER = str_constructor.FormatMap(
    '{stdin} set in {phase_setup}:',
    {
        'stdin': misc_texts.STDIN.capitalize(),
        'phase_setup': phase_infos.SETUP.name.syntax,
    }
)

_NOTES = """\
If the {atc} is a {PROGRAM} that itself defines {stdin},
then the {stdin} set here is appended to the {stdin}
defined by the {PROGRAM}.

(This requires that the {actor} is {run_program_actor}.) 
"""
