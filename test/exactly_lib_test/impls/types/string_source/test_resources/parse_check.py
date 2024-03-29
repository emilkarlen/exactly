from exactly_lib.impls.types.string_source import parse
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.type_val_deps.types.path.rel_opts_configuration import RelOptionsConfiguration
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker


def rel_opts_conf_of_single(default_relativity: RelOptionType) -> RelOptionsConfiguration:
    return RelOptionsConfiguration(
        PathRelativityVariants({default_relativity}, False),
        default_relativity,
    )


ARBITRARY_FILE_RELATIVITIES = rel_opts_conf_of_single(RelOptionType.REL_ACT)


def just_parse(source: ParseSource,
               accepted_file_relativities: RelOptionsConfiguration = ARBITRARY_FILE_RELATIVITIES,
               ):
    parse.string_source_parser(accepted_file_relativities).parse(source)


def checker(accepted_file_relativities: RelOptionsConfiguration = ARBITRARY_FILE_RELATIVITIES
            ) -> parse_checker.Checker:
    return parse_checker.Checker(
        ParserAsLocationAwareParser(
            parse.string_source_parser(accepted_file_relativities)
        )
    )
