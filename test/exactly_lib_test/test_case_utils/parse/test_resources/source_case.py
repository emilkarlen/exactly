from typing import TypeVar, Generic

from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

SOURCE = TypeVar('SOURCE')


class SourceCase(Generic[SOURCE]):
    def __init__(self,
                 name: str,
                 source: SOURCE,
                 source_assertion: asrt.ValueAssertion[SOURCE]):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
