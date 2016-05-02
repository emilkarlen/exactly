from exactly_lib.help.concepts.contents_structure import PlainConceptDocumentation, Name
from exactly_lib.help.utils.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.help.utils.phase_names import CONFIGURATION_PHASE_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class _PreprocessorConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('preprocessor', 'preprocessors'))

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(
            Description(text(_SINGLE_LINE_DESCRIPTION.format(CONFIGURATION_PHASE_NAME)),
                        normalize_and_parse(_DESCRIPTION_REST)))


PREPROCESSOR_CONCEPT = _PreprocessorConcept()

_SINGLE_LINE_DESCRIPTION = """\
A program that may transform a test case file before it is processed."""

_DESCRIPTION_REST = """\
A preprocessor is an executable program, with optional command line arguments.


It is given a single argument - the name of the test case file that it should process.


It must output the result of the processing on stdout.


An exit code other than 0 indicates error.
"""
