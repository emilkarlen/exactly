from typing import List

from exactly_lib.help.entities.directives.contents_structure import DirectiveDocumentation
from exactly_lib.help.entities.directives.objects.file_inclusion import FileInclusionDocumentation


def all_directives() -> List[DirectiveDocumentation]:
    return [
        FileInclusionDocumentation(),
    ]
