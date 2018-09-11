from exactly_lib.help.program_modes.common.contents_structure import SectionInstructionSet
from exactly_lib.help.program_modes.test_suite.section.common import \
    TestSuiteSectionDocumentationForSectionWithInstructions
from exactly_lib.util.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import structures as docs


class ConfigurationSectionDocumentation(TestSuiteSectionDocumentationForSectionWithInstructions):
    def __init__(self,
                 name: str,
                 instruction_set: SectionInstructionSet):
        super().__init__(name, instruction_set)

    def instruction_purpose_description(self) -> list:
        return []

    def is_mandatory(self) -> bool:
        return False

    def contents_description(self) -> list:
        return normalize_and_parse(_CONTENTS_DESCRIPTION)

    def purpose(self) -> Description:
        return Description(docs.text(_PURPOSE_SINGLE_LINE_DESCRIPTION_TEXT),
                           normalize_and_parse(_PURPOSE_REST_TEXT))


_PURPOSE_SINGLE_LINE_DESCRIPTION_TEXT = 'Configures how individual test case are executed.'

_PURPOSE_REST_TEXT = """\
The configuration is used for all test cases listed in the file, but not for test cases in sub suites.
"""

_CONTENTS_DESCRIPTION = """\
Contains a sequence of instructions.


Each instruction starts on a new line with the name of the instruction.

After the instruction name follows options and arguments, who's syntax is specific for each instruction.


Instructions uses syntax for options and arguments that resembles that of unix shells.
"""
