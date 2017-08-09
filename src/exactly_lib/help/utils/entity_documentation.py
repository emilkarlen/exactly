"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""

from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId, CrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text


class EntityDocumentation:
    """
    Base class for documentation of "entities" with a name and single-line-description.
    """

    def singular_name(self) -> str:
        """
        Name of the entity in singular.
        """
        raise NotImplementedError()

    def single_line_description(self) -> Text:
        """
        A short description of the entity.
        """
        raise NotImplementedError()

    def cross_reference_target(self) -> CrossReferenceId:
        raise NotImplementedError()


class EntityDocumentationBase(EntityDocumentation):
    def __init__(self, name_and_cross_ref_target: SingularNameAndCrossReferenceId):
        self._name_and_cross_ref_target = name_and_cross_ref_target

    def singular_name(self) -> str:
        return self._name_and_cross_ref_target.singular_name

    def single_line_description_str(self) -> str:
        return self._name_and_cross_ref_target.single_line_description_str

    def cross_reference_target(self) -> CrossReferenceId:
        return self._name_and_cross_ref_target.cross_reference_target

    def single_line_description(self) -> Text:
        return docs.text(self.single_line_description_str())

    def name_and_single_line_description(self) -> Text:
        return docs.text(self.name_and_single_line_description_str())

    def name_and_single_line_description_str(self) -> str:
        return formatting.entity(self.singular_name()) + ' - ' + self.single_line_description_str()


class EntitiesHelp(tuple):
    def __new__(cls,
                entity_type_name: str,
                entities: iter):
        """
        :type entities: [`EntityDocumentation`]
        """
        return tuple.__new__(cls, (entity_type_name, list(entities)))

    @property
    def entity_type_name(self) -> str:
        """
        Name of entity.
        """
        return self[0]

    @property
    def all_entities(self) -> list:
        """
        :type: [`EntityDocumentation`]
        """
        return self[1]
