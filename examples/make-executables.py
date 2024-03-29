import itertools

from make import *

########################################
# Programs
########################################

DO_NOTHING = 'do-nothing'

HELLO_WORLD__WRITE_TO_FILE_ARG = 'hello-world'

HELLO_WORLD = 'helloworld'

PRINT_NUMBER_OF_ARGUMENTS = 'print-number-of-arguments'

PRINT_NUMBER_OF_LINES_IN_FILE = 'print-number-of-lines-in-file'

PRINT_ONE_ARGUMENT_PER_LINE = 'print-one-argument-per-line'

CLASSIFY_FILES = 'classify-files-by-moving-to-appropriate-dir'

COPY_STDIN_TO_STDOUT = 'copy-stdin-to-stdout'

FILTER_LINES = 'filter-lines'

LIST_FILES_UNDER_CURRENT_DIRECTORY = 'list-files-under-current-directory'

REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY = 'remove-all-files-in-the-current-directory'

DO_SOMETHING_GOOD_WITH = 'do-something-good-with'

SYSTEM_UNDER_TEST = 'system-under-test'

MY_SETUP_HELPER_PROGRAM = 'my-setup-helper-program'

MY_ASSERT_HELPER_PROGRAM = 'my-assert-helper-program'

MY_STRING_TRANSFORMER_PROGRAM = 'my-text-transformer-program'

MY_HELPER_PROGRAM = 'my-helper-program'

MANIPULATE_DATABASE_CONTENTS = 'manipulate-database-contents'

PRINT_ENVIRONMENT_VARIABLES = 'print-environment-variables'

MY_CONTACTS_PROGRAM = 'my-contacts-program'

PROGRAM_THAT_WRITES_LOG_FILE = 'program-that-writes-log-file'

########################################
# Directories
########################################

src_base_dir = Path('executables-src')
first_step_dir = Path('first-step')
sandbox_dir = Path('sandbox-directories')
symbols_dir = Path('symbols')
home_dir = Path('home-directories')
cleanup_dir = Path('cleanup')
dir_contents_dir = Path('dir-contents')
external_programs_dir = Path('external-programs')
setup_dir = Path('setup')
file_transformations_dir = Path('file-transformations')
suites_dir = Path('suites')

readme_contacts_dir = Path('contacts')
readme_classify_dir = Path('classify')
readme_sandbox_dir = Path('sandbox')
readme_ext_pgm_dir = Path('external-programs')


########################################
# Directories setup
########################################

def st(target_base: Path, file_name: str) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / file_name,
                           target_base / file_name)


def sts(target_base: Path, file_names: List[str]) -> List[SourceAndTarget]:
    return [st(target_base, file_name) for file_name in file_names]


def do_nothing(target_file: Path) -> SourceAndTarget:
    return SourceAndTarget(src_base_dir / DO_NOTHING,
                           target_file)


def do_nothing_list(target_base: Path, target_file_names: List[str]) -> List[SourceAndTarget]:
    return [do_nothing(target_base / file_name) for file_name in target_file_names]


README_FILES: Iterable[SourceAndTarget] = itertools.chain.from_iterable([
    sts(readme_contacts_dir,
        [MY_CONTACTS_PROGRAM,
         ]),
    sts(readme_classify_dir,
        [CLASSIFY_FILES,
         ]),
    sts(readme_sandbox_dir,
        [HELLO_WORLD__WRITE_TO_FILE_ARG,
         ]),
    sts(Path('bin'),
        [FILTER_LINES,
         ]),
    do_nothing_list(
        readme_ext_pgm_dir,
        [MY_ASSERT_HELPER_PROGRAM,
         MY_SETUP_HELPER_PROGRAM,
         MY_STRING_TRANSFORMER_PROGRAM,
         SYSTEM_UNDER_TEST,
         ]),
    sts(
        readme_ext_pgm_dir / 'bin',
        ['mysql']),
    sts(Path('transform'),
        [PROGRAM_THAT_WRITES_LOG_FILE]
        ),
    sts(Path('git-hook'),
        ['prepare-commit-msg']
        ),
])

BUILTIN_HELP_FILES: Iterable[SourceAndTarget] = [
    st(Path('.'), HELLO_WORLD),
]

INTRO_FILES: Iterable[SourceAndTarget] = itertools.chain.from_iterable(
    [
        sts(first_step_dir,
            [HELLO_WORLD__WRITE_TO_FILE_ARG,
             FILTER_LINES,
             ]),

        sts(Path('actors') / 'bin',
            [HELLO_WORLD__WRITE_TO_FILE_ARG,
             ]),

        sts(sandbox_dir,
            [HELLO_WORLD__WRITE_TO_FILE_ARG,
             CLASSIFY_FILES,
             REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY,
             ]),

        sts(symbols_dir / 'bin',
            [PRINT_NUMBER_OF_ARGUMENTS,
             PRINT_ONE_ARGUMENT_PER_LINE,
             CLASSIFY_FILES,
             PRINT_NUMBER_OF_LINES_IN_FILE,
             FILTER_LINES,
             ]),

        sts(file_transformations_dir / 'bin',
            [PRINT_ONE_ARGUMENT_PER_LINE,
             ]),

        do_nothing_list(cleanup_dir,
                        [MANIPULATE_DATABASE_CONTENTS,
                         MY_HELPER_PROGRAM,
                         ]),

        do_nothing_list(external_programs_dir,
                        [MY_ASSERT_HELPER_PROGRAM,
                         MY_SETUP_HELPER_PROGRAM,
                         'my-program-that-reads-stdin',
                         ]),

        do_nothing_list(home_dir / 'bin',
                        [DO_SOMETHING_GOOD_WITH,
                         ]),

        sts(setup_dir,
            [COPY_STDIN_TO_STDOUT,
             REMOVE_ALL_FILES_IN_THE_CURRENT_DIRECTORY,
             PRINT_ENVIRONMENT_VARIABLES,
             LIST_FILES_UNDER_CURRENT_DIRECTORY,
             ]),
    ])

WIKI_FILES: Iterable[SourceAndTarget] = itertools.chain.from_iterable(
    [
        sts(Path(HELLO_WORLD__WRITE_TO_FILE_ARG),
            [HELLO_WORLD__WRITE_TO_FILE_ARG,
             ]),

    ])

REAL_WORLD_FILES: Iterable[SourceAndTarget] = itertools.chain.from_iterable(
    [
        sts(Path('git-hook'),
            ['prepare-commit-msg']
            ),
    ])

SUB_DIR_CONFIGS: List[Tuple[str, Iterable[SourceAndTarget]]] = [
    ('intro', INTRO_FILES),
    ('readme-file-examples', README_FILES),
    ('builtin-help', BUILTIN_HELP_FILES),
    ('wiki', WIKI_FILES),
    ('real-world', REAL_WORLD_FILES),
]

if __name__ == '__main__':
    main(SUB_DIR_CONFIGS)
