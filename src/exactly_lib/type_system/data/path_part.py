class PathPart:
    """
    The relative path that follows the root path of the `FileRef`.
    """

    def value(self) -> str:
        raise NotImplementedError()
