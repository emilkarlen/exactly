from exactly_lib.cli.definitions.program_modes.test_case import command_line_options as opt
from exactly_lib.util.cli_syntax.elements import argument as arg

TEST_CASE_FILE_ARGUMENT = arg.Named(opt.TEST_CASE_FILE_ARGUMENT)

PREPROCESSOR_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_PREPROCESSOR__LONG,
                                            argument=opt.PREPROCESSOR_OPTION_ARGUMENT)

SUITE_OPTION = arg.short_long_option(long_name=opt.OPTION_FOR_SUITE__LONG,
                                     argument=opt.SUITE_OPTION_METAVAR)

FILES_DESCRIPTION_WITH_DEFAULT_SUITE = """\
If there exists a file "{default_suite_file}" in the same directory as {TEST_CASE_FILE},
then this file must be a test suite, and the test case is run as part of this suite. 
"""
