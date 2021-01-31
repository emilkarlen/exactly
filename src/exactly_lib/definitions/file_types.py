from exactly_lib.util.str_ import name
from exactly_lib.util.str_.name import NameWithGenderWithFormatting

REGULAR = NameWithGenderWithFormatting(name.a_name_with_plural_s('regular file'))

DIRECTORY = NameWithGenderWithFormatting(name.NameWithGender('a', 'directory', 'directories'))

SYM_LINK = NameWithGenderWithFormatting(name.a_name_with_plural_s('symbolic link'))
