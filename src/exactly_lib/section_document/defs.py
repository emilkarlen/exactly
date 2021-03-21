from exactly_lib.util.str_ import name

DESCRIPTION_DELIMITER = '`'

DESCRIPTION_DELIMITER_CHAR_NAME = name.NameWithGenderWithFormatting(
    name.a_name(name.name_with_plural_s('backtick'))
)
END_OF_FILE = 'END-OF-FILE'
END_OF_LINE = 'END-OF-LINE'

INSTRUCTION = name.NameWithGenderWithFormatting(
    name.an_name(name.name_with_plural_s('instruction'))
)

INSTRUCTION_DESCRIPTION = name.NameWithGenderWithFormatting(
    name.an_name(name.name_with_plural_s('instruction description'))
)


def format_constant(constant: str) -> str:
    return '"' + constant + '"'
