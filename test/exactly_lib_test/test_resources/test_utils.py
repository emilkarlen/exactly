class EA:
    """One expected value and one actual value."""

    def __init__(self,
                 expected,
                 actual):
        self.expected = expected
        self.actual = actual


class NEA:
    """A name, one expected value and one actual value."""

    def __init__(self,
                 name: str,
                 expected,
                 actual):
        self.name = name
        self.expected = expected
        self.actual = actual


class NIE:
    """A name, one expected value and one input value."""

    def __init__(self,
                 name: str,
                 expected_value,
                 input_value):
        self.name = name
        self.expected_value = expected_value
        self.input_value = input_value
