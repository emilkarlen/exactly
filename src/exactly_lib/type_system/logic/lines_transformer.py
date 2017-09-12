from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds


class LinesTransformer:
    """
    Transforms a sequence of lines, where each line is a string.
    """

    @property
    def is_identity_transformer(self) -> bool:
        """
        Tells if this transformer is the identity transformer
        """
        return False

    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return type(self).__name__
