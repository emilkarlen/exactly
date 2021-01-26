from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


def notes_on_when_to_use_run_instruction() -> SectionContents:
    tp = TextParser({
        'stdin': misc_texts.STDIN,
        'exit_code': misc_texts.EXIT_CODE,
        'run_program': formatting.InstructionName(instruction_names.RUN_INSTRUCTION_NAME),
        'instruction': concepts.INSTRUCTION_CONCEPT_INFO.singular_name,
    })
    return tp.section_contents(_WHEN_TO_USE_RUN)


_WHEN_TO_USE_RUN = """
If {stdin} must be supplied,
or the {exit_code} should be ignored,
then use the {run_program} {instruction}.
"""
