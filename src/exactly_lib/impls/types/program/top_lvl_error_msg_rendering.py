from exactly_lib.common.report_rendering import header_blocks
from exactly_lib.common.report_rendering.description_tree import rendering__node_wo_data
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import types
from exactly_lib.impls import texts
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.render import combinators
from exactly_lib.util.render.renderer import Renderer
from exactly_lib.util.simple_textstruct.rendering import component_renderers as comp_rend, blocks, line_objects
from exactly_lib.util.simple_textstruct.structure import MajorBlock, MinorBlock
from exactly_lib.util.str_.formatter import StringFormatter


def header_and_program_block(header: str, program: StructureRenderer) -> Renderer[MajorBlock]:
    return header_blocks.w_details(header, rendering__node_wo_data.NodeAsMinorBlocksRenderer(program))


def unable_to_execute_program(program: StructureRenderer,
                              explanation: TextRenderer) -> TextRenderer:
    return combinators.PrependR(
        header_and_program_block(_UNABLE_TO_EXECUTE_HEADER, program),
        explanation
    )


def stderr_contents_block(stderr_contents: str) -> Renderer[MinorBlock]:
    if not stderr_contents:
        stderr_contents = '<empty>'
    return comp_rend.MinorBlockR(
        combinators.SequenceR([
            comp_rend.LineElementR(line_objects.PreFormattedString(texts.OUTPUT_ON_STDERR__HEADER)),
            comp_rend.LineElementR(line_objects.PreFormattedString.of_str(stderr_contents)),
        ])
    )


def non_zero_exit_code_msg(program: StructureRenderer,
                           exit_code: int,
                           stderr_contents: str) -> TextRenderer:
    return combinators.SequenceR([
        header_and_program_block(_NON_ZERO_EXIT_CODE_HEADER, program),
        _actual_exit_code_and_stderr_block(exit_code, stderr_contents),
    ]
    )


def _actual_exit_code_line(exit_code: int) -> str:
    return _EXIT_CODE_LINE_PREFIX + str(exit_code)


def _actual_exit_code_and_stderr_block(exit_code: int,
                                       stderr_contents: str
                                       ) -> Renderer[MajorBlock]:
    def exit_code_block() -> Renderer[MinorBlock]:
        return blocks.MinorBlockOfSingleLineObject(
            line_objects.PreFormattedString(_actual_exit_code_line(exit_code))
        )

    minor_blocks = [
        exit_code_block(),
    ]
    if stderr_contents:
        minor_blocks.append(stderr_contents_block(stderr_contents))

    return comp_rend.MajorBlockR(
        combinators.SequenceR(minor_blocks)
    )


_STRING_FORMATTER = StringFormatter({
    'exit_code': misc_texts.EXIT_CODE,
    'program': types.PROGRAM_TYPE_INFO.name,
})

_NON_ZERO_EXIT_CODE_HEADER = _STRING_FORMATTER.format(
    'Non-zero {exit_code} from {program}'
)

_UNABLE_TO_EXECUTE_HEADER = _STRING_FORMATTER.format(
    'Unable to execute {program}'
)

_EXIT_CODE_LINE_PREFIX = misc_texts.EXIT_CODE_TITLE + ': '
