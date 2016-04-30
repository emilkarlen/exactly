from exactly_lib.help.concepts.concept_structure import PlainConceptDocumentation, Name
from exactly_lib.help.utils.description import Description
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure.structures import text


class _EnvironmentVariableConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(Name('environment variable', 'environment variables'))

    def purpose(self) -> Description:
        return Description(text(_ENVIRONMENT_VARIABLE_SINGLE_LINE_DESCRIPTION),
                           normalize_and_parse(_ENVIRONMENT_VARIABLE_REST_DESCRIPTION))


_ENVIRONMENT_VARIABLE_SINGLE_LINE_DESCRIPTION = """\
Environment variables that are available to instructions."""

_ENVIRONMENT_VARIABLE_REST_DESCRIPTION = """\
TODO _ENVIRONMENT_VARIABLE_REST_DESCRIPTION"""

ENVIRONMENT_VARIABLE_CONCEPT = _EnvironmentVariableConcept()
