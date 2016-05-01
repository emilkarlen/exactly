from exactly_lib.help.concepts.concept_structure import ConceptDocumentation


class ConceptsHelp(tuple):
    def __new__(cls,
                concepts: iter):
        """
        :type concepts: [`ConceptDocumentation`]
        """
        return tuple.__new__(cls, (list(concepts),))

    @property
    def all_concepts(self) -> list:
        """
        :type: [`ConceptDocumentation`]
        """
        return self[0]

    def lookup_by_name_in_singular(self, concept_name: str) -> ConceptDocumentation:
        matches = list(filter(lambda c: c.name().singular == concept_name, self.all_concepts))
        if not matches:
            raise KeyError('Not a concept: ' + concept_name)
        return matches[0]