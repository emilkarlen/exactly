from exactly_lib.common.help.see_also import SeeAlsoSet
from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.entity_names import SYNTAX_ELEMENT_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId


class SyntaxElementDocumentation(EntityDocumentationBase):
    def __init__(self,
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                 main_description_rest: list,
                 invokation_variants: list,
                 see_also_cross_refs: SeeAlsoSet):
        """

        :param name_and_cross_ref_target:
        :param main_description_rest:
        :param invokation_variants:
        :param see_also_cross_refs: [:class:`CrossReferenceId`]
        """
        super().__init__(name_and_cross_ref_target)
        self._main_description_rest = main_description_rest
        self._invokation_variants = invokation_variants
        self._see_also_cross_refs = see_also_cross_refs

    def main_description_rest(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        return self._main_description_rest

    def invokation_variants(self) -> list:
        """
        :rtype [`InvokationVariant`]
        """
        return self._invokation_variants

    def see_also_items(self) -> list:
        """
        :rtype: [`SeeAlsoItem`]
        """
        return self._see_also_cross_refs.see_also_items


def syntax_elements_help(syntax_elements: iter) -> EntitiesHelp:
    """
    :param syntax_elements: [SyntaxElementDocumentation]
    """
    return EntitiesHelp(SYNTAX_ELEMENT_ENTITY_TYPE_NAME, syntax_elements)
