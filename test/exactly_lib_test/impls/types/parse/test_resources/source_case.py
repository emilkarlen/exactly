from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class SourceCase:
    def __init__(self,
                 name: str,
                 source,
                 source_assertion: Assertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion


class SourceCase2:
    def __init__(self,
                 name: str,
                 source,
                 source_assertion: Assertion,
                 other_assertion: Assertion):
        self.name = name
        self.source = source
        self.source_assertion = source_assertion
        self.other_assertion = other_assertion
