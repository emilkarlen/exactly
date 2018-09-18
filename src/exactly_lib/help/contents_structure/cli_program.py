from typing import List, Optional

from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.section_document.model import SectionContents
from exactly_lib.util.cli_syntax.elements.cli_program_syntax import Synopsis, DescribedArgument
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.structure.core import ParagraphItem


class CliProgramSyntaxDocumentation:
    def __init__(self, program_name: str):
        self.program_name = program_name

    def description(self) -> DescriptionWithSubSections:
        raise NotImplementedError()

    def initial_paragraphs(self) -> List[ParagraphItem]:
        return []

    def synopsises(self) -> List[Synopsis]:
        raise NotImplementedError()

    def argument_descriptions(self) -> List[DescribedArgument]:
        return []

    def files(self) -> Optional[SectionContents]:
        return None

    def outcome(self, environment: ConstructionEnvironment) -> Optional[SectionContents]:
        return None

    def see_also(self) -> List[SeeAlsoTarget]:
        return []
