from exactly_lib.util.str_ import name

INTEGER_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.an_name_with_plural_s('integer'))
LINE_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('line'))
FILE_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('file'))
TEXT_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('text'))
FILES_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name(name.Name('set of files', 'sets of files')))
