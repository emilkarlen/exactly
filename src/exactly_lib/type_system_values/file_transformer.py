from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds


class FileTransformer:
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('abstract method')


class IdentityFileTransformer(FileTransformer):
    def transform(self, tcds: HomeAndSds, lines: iter) -> iter:
        raise NotImplementedError('this method should never be called')


class CustomFileTransformer(FileTransformer):
    """
    Base class for built in custom transformers.

    Such a transformer is identified by its name,
    that must be unique.
    """

    def __init__(self, name: str):
        self.name = name


class FileTransformerStructureVisitor:
    """
    Visits all variants of :class:`FileSelector`.

    The existence of this class means that the structure of :class:`FileSelector`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, transformer: FileTransformer):
        if isinstance(transformer, CustomFileTransformer):
            return self.visit_custom(transformer)
        elif isinstance(transformer, IdentityFileTransformer):
            return self.visit_identity(transformer)
        else:
            raise TypeError('Unknown {}: {}'.format(FileTransformer,
                                                    str(transformer)))

    def visit_custom(self, transformer: CustomFileTransformer):
        raise NotImplementedError('abstract method')

    def visit_identity(self, transformer: IdentityFileTransformer):
        raise NotImplementedError('abstract method')
