from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class SourceCase:
    def __init__(self,
                 name: str,
                 source: ParseSource,
                 source_assertion: asrt.ValueAssertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
