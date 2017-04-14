class PathPart:
    """
    The relative path that follows the root path of the `FileRef`.
    """

    def resolve(self) -> str:
        raise NotImplementedError()
