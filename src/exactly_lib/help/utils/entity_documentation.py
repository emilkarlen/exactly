"""
Utilities for generating documentation for "entities" - things with a name and single-line-description.

Makes it possible to reuse some code for generating documentation.
"""

from exactly_lib.help_texts import formatting
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId, CrossReferenceId, EntityTypeNames
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import Text, ConcreteText


class EntityDocumentation:
    """
    Base class for documentation of "entities" with a name and single-line-description.
    """

    def singular_name(self) -> str:
        """
        Name of the entity in singular.
        """
        raise NotImplementedError()

    @property
    def singular_name_text(self) -> ConcreteText:
        return docs.text(self.singular_name())

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

    @property
    def name_and_cross_ref_target(self) -> SingularNameAndCrossReferenceId:
        return self._name_and_cross_ref_target

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
                names: EntityTypeNames,
                entities: iter):
        """
        :type entities: [`EntityDocumentation`]
        """
        return tuple.__new__(cls, (names,
                                   list(entities)))

    @property
    def names(self) -> EntityTypeNames:
        return self[0]

    @property
    def all_entities(self) -> list:
        """
        :type: [`EntityDocumentation`]
        """
        return self[1]


def cross_reference_id_list(entity_documentation_iterable) -> list:
    return [x.cross_reference_target()
            for x in entity_documentation_iterable]
