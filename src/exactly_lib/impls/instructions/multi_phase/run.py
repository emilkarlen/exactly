from typing import List, Sequence, Callable

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, types
from exactly_lib.definitions.primitives import program as program_primitives
from exactly_lib.impls import texts
from exactly_lib.impls.instructions.multi_phase.utils import \
    instruction_from_parts_for_executing_program as spe_parts
from exactly_lib.impls.instructions.multi_phase.utils import instruction_part_utils
from exactly_lib.impls.instructions.multi_phase.utils.assert_phase_info import \
    IsBothAssertionAndHelperIfInAssertPhase
from exactly_lib.impls.instructions.multi_phase.utils.instruction_from_parts_for_executing_program import \
    ExecutionResultAndStderr
from exactly_lib.impls.instructions.multi_phase.utils.instruction_parts import \
    InstructionPartsParser, InstructionParts
from exactly_lib.impls.types.parse import options as option_parsing
from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents

IGNORE_EXIT_CODE_OPTION_NAME = program_primitives.WITH_IGNORED_EXIT_CODE_OPTION_NAME


def parts_parser(instruction_name: str) -> InstructionPartsParser:
    return _InstructionPartsParser(instruction_name)


def embryo_parser(instruction_name: str) -> spe_parts.InstructionEmbryoParser:
    return spe_parts.InstructionEmbryoParser(
        instruction_name,
        parse_program.program_parser()
    )


NON_ASSERT_PHASE_OUTCOME = texts.run_outcome__with_ignored_exit_code_option

NON_ASSERT_PHASE_SINGLE_LINE_DESCRIPTION = 'Runs {program_type:a/q}'.format_map({
    'program_type': types.PROGRAM_TYPE_INFO.name
})


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  IsBothAssertionAndHelperIfInAssertPhase):
    def __init__(self,
                 name: str,
                 single_line_description: str,
                 outcome: Callable[[], Sequence[ParagraphItem]],
                 ):
        self._outcome = outcome
        super().__init__(name, {
            'program_type': types.PROGRAM_TYPE_INFO.name
        })
        self._single_line_description = single_line_description

    def single_line_description(self) -> str:
        return self._single_line_description

    def outcome(self) -> SectionContents:
        return SectionContents(list(self._outcome()))

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.OPTIONAL, a.Option(IGNORE_EXIT_CODE_OPTION_NAME)),
                a.Single(a.Multiplicity.MANDATORY, syntax_elements.PROGRAM_SYNTAX_ELEMENT.argument),
            ]),
        ]

    def notes(self) -> SectionContents:
        return self._tp.section_contents(texts.THE_PROGRAM_TYPE_MUST_TERMINATE_SENTENCE)

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        name_and_cross_ref_list = [
            types.PROGRAM_TYPE_INFO,
            syntax_elements.PROGRAM_SYNTAX_ELEMENT,
        ]
        return cross_reference_id_list(name_and_cross_ref_list)


class _InstructionPartsParser(InstructionPartsParser):
    _IGNORE_EXIT_CODE_OPTION_PARSER = option_parsing.option_is_present(IGNORE_EXIT_CODE_OPTION_NAME)

    def __init__(self, instruction_name: str):
        self._embryo_parser = embryo_parser(instruction_name)

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> InstructionParts:
        result_translator = self._parse_result_translator(source)
        embryo = self._embryo_parser.parse(fs_location_info, source)
        return instruction_part_utils.instruction_parts_from_embryo(
            embryo,
            result_translator,
        )

    def _parse_result_translator(self,
                                 source: ParseSource,
                                 ) -> spe_parts.MainStepResultTranslator[ExecutionResultAndStderr]:
        ignore_exit_code = self._IGNORE_EXIT_CODE_OPTION_PARSER.parse(source)
        return (
            instruction_part_utils.MainStepResultTranslatorForUnconditionalSuccess()
            if ignore_exit_code
            else
            spe_parts.ResultTranslator()
        )
