from exactly_lib.definitions.primitives import file_matcher
from . import parse, properties

WHOLE_PATH_PARSER = parse.parser(
    properties.WholePathAsPathPropertyGetter(),
    properties.WholePathAsStrPropertyGetter(),
)

NAME_PARSER = parse.parser_for_name_part(
    file_matcher.NAME_MATCHER_NAME,
    properties.get_name_from_name,
)

STEM_PARSER = parse.parser_for_name_part(
    file_matcher.STEM_MATCHER_NAME,
    properties.get_stem_from_name,
)

SUFFIXES_PARSER = parse.parser_for_name_part(
    file_matcher.SUFFIXES_MATCHER_NAME,
    properties.get_suffixes_from_name,
)

SUFFIX_PARSER = parse.parser_for_name_part(
    file_matcher.SUFFIX_MATCHER_NAME,
    properties.get_suffix_from_name,
)
