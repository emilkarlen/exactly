class WithOptionDescription:
    """Describes the option/config of an object,
    for the purpose of error messages to the end user."""

    @property
    def option_description(self) -> str:
        raise NotImplementedError('abstract method')
