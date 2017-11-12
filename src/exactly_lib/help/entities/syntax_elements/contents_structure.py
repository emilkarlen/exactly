from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase, EntityTypeNames
from exactly_lib.help_texts import entity_names
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help_texts.names.formatting import syntax_element
from exactly_lib.util import name

SYNTAX_ELEMENT_ENTITY_TYPE_NAMES = EntityTypeNames(
    name.name_with_plural_s('syntax element'),
    entity_names.SYNTAX_ELEMENT_ENTITY_TYPE_NAME,
    syntax_element('syntax element'))


class SyntaxElementDocumentation(EntityDocumentationBase):
    def __init__(self,
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId):
        super().__init__(name_and_cross_ref_target)

    def main_description_rest(self) -> list:
        """
        :rtype [`ParagraphItem`]
        """
        raise NotImplementedError('abstract method')

    def invokation_variants(self) -> list:
        """
        :rtype [`InvokationVariant`]
        """
        raise NotImplementedError('abstract method')

    def syntax_element_descriptions(self) -> list:
        """
        :rtype [`SyntaxElementDescription`]
        """
        raise NotImplementedError('abstract method')

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        raise NotImplementedError('abstract method')


class SyntaxElementDocumentationWithConstantValues(SyntaxElementDocumentation):
    def __init__(self,
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                 main_description_rest: list,
                 invokation_variants: list,
                 syntax_element_descriptions: list,
                 see_also_targets: list):
        super().__init__(name_and_cross_ref_target)
        self._main_description_rest = main_description_rest
        self._invokation_variants = invokation_variants
        self._syntax_element_descriptions = syntax_element_descriptions
        self._see_also_targets = see_also_targets

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

    def syntax_element_descriptions(self) -> list:
        return self._syntax_element_descriptions

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return self._see_also_targets


def syntax_element_documentation(name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                                 main_description_rest: list,
                                 invokation_variants: list,
                                 syntax_element_descriptions: list,
                                 see_also_targets: list) -> SyntaxElementDocumentation:
    return SyntaxElementDocumentationWithConstantValues(name_and_cross_ref_target,
                                                        main_description_rest,
                                                        invokation_variants,
                                                        syntax_element_descriptions,
                                                        see_also_targets)


def syntax_elements_help(syntax_elements: iter) -> EntitiesHelp:
    """
    :param syntax_elements: [SyntaxElementDocumentation]
    """
    return EntitiesHelp(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
                        syntax_elements)
