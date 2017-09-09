from exactly_lib.util.with_option_description import WithOptionDescription


class Matcher(WithOptionDescription):
    """Matches a model."""

    def matches(self, model) -> bool:
        raise NotImplementedError('abstract method')
