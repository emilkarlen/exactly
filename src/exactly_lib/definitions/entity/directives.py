from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.definitions.cross_ref.concrete_cross_refs import EntityCrossReferenceId
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.doc_format import syntax_text
from exactly_lib.definitions.entity.all_entity_types import DIRECTIVE_ENTITY_TYPE_NAMES
from exactly_lib.util.textformat.structure.core import StringText


class DirectiveInfo(SingularNameAndCrossReferenceId):
    def __init__(self,
                 singular_name: str,
                 single_line_description_str: str,
                 cross_reference_target: CrossReferenceId):
        super().__init__(singular_name,
                         single_line_description_str,
                         cross_reference_target)

    @property
    def singular_name_text(self) -> StringText:
        return syntax_text(self._singular_name)


def directive_cross_ref(name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(DIRECTIVE_ENTITY_TYPE_NAMES,
                                  name)


def name_and_ref_target(name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return DirectiveInfo(name,
                         single_line_description_str,
                         directive_cross_ref(name))


INCLUDING_DIRECTIVE_INFO = name_and_ref_target('including',
                                               'Includes test case contents from an external file')

ALL_DIRECTIVES = [
    INCLUDING_DIRECTIVE_INFO,
]
