import enum


class ModificationType(enum.Enum):
    CREATE = 1
    APPEND = 2


class FileType(enum.Enum):
    REGULAR = 1
    DIR = 2
