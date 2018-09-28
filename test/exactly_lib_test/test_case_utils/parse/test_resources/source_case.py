from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SourceCase:
    def __init__(self,
                 name: str,
                 source,
                 source_assertion: ValueAssertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion


class SourceCase2:
    def __init__(self,
                 name: str,
                 source,
                 source_assertion: ValueAssertion,
                 other_assertion: ValueAssertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.other_assertion = other_assertion
