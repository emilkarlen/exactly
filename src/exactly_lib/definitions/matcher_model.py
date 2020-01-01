from exactly_lib.util import name

LINE_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('line'))
FILE_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('file'))
STRING_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name_with_plural_s('string'))
FILES_MATCHER_MODEL = name.NameWithGenderWithFormatting(name.a_name(name.Name('set of files', 'sets of files')))
