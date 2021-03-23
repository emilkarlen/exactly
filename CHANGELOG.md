# ChangeLog


The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html),
with exception of a "0." prefix until version 1 is released.

## [0.15.0] - 2021-03-23

### Added

 - Type `files-source` - Produces a set of files (for populating a directory)   
 - Instruction `dir` - Populate a dir with contents given by a `files-source`
 - Instruction `file` - Append contents to existing file
 - Instruction `def` - `string` - Form `:> TEXT-UNTIL-END-OF-LINE`
 - Type `text-source` - Form `:> TEXT-UNTIL-END-OF-LINE`
 - Syntax element `REGEX` - Form `:> TEXT-UNTIL-END-OF-LINE`
 - Syntax element `PROGRAM-ARGUMENT` - Form `HERE-DOCUMENT`

### Changed

 - Default timeout - Set to 60s
 - Instruction `dir` - Fails if the directory already exists (breaking)
 - Type `string` - Reserved words
 - Type `list` - `)` ends list
 - Type `list` - Multi line list using backslash
 - Syntax elements `PROGRAM-ARGUMENT` - Reserved words
 - Syntax elements `PROGRAM-ARGUMENT` - `)` ends list
 - Syntax elements `PROGRAM-ARGUMENT` - Multi line list using backslash

### Removed

 - Syntax element `PATH` - Optional surrounding by parentheses

## [0.14.0] - 2021-03-01

### Added

 - Instruction `setup`/`env` - Ability to set variables separately for the `action to check` 
 - Instruction `timeout` - Ability to set no-timeout
 - Type `text-source` (together with improvements of corresponding element `TEXT-SOURCE`)   
 - Type `text-transformer` - `grep` - Shortcut for `filter contents matches`
 - Type `text-transformer` - `replace` - `-at LINE-MATCHER` - Limits replacement to certain lines

### Changed

 - Instruction `setup`/`env` - VALUE argument is a `text-source`
 - Instruction `conf`/`timeout` - Move to later phases (breaking)
 - Type `string-matcher`     - Rename to `text-matcher` (breaking)
 - Type `string-transformer` - Rename to `text-transformer` (breaking)

### Removed

 - Support of Python v 3.5

## [0.13.0] - 2021-02-07

### Added

 - Interpreter actors - interpreter `% STRING [PROGRAM-ARGUMENT]...`
 - Interpreter actors - interpreter `-python [PROGRAM-ARGUMENT]...`
 - Instruction `conf`/`actor` - Ability to set the "null" actor
 - Instruction `%`
 - Instruction `copy` - Available in all phases
 - Instruction `exit-code` - Option to check exit code from arbitrary program
 - Type `file-matcher` - `path` - matches the absolute path of files
 - Type `file-matcher` - `stem` - matches the "stem" part of file names
 - Type `file-matcher` - `suffixes` - matches the "suffixes" part of file names
 - Type `file-matcher` - `suffix` - matches the "suffix" part of file names
 - Type `line-matcher` - `contents` - matches text contents using a `string-matcher`
 - Type `string-transformer` - `char-case`
 - Type `string-transformer` - `replace-test-case-dirs`
 - Type `string-transformer` - `strip`
 - Type `string-transformer` - `filter` - `-line-nums` Matches lines against line number ranges
 - Type `string-matcher` - Add alias `~` for `matches`
 - Type `string-matcher` - Add alias `==` for `equals`
 - Type `program` - `-stdin` - Ability to set stdin
 - Type `integer-matcher`
 - Syntax element `STRING-SOURCE`
 - Builtin symbol - string `NEW_LINE`

### Changed

 - Syntax of type expressions in nested expressions - May not contain binary operators (unless inside parentheses) (breaking)
 - Syntax of type expressions - Precedences of `||` and `&&` (breaking)
 - Type `files-matcher` - rename `-prune` -> `-with-pruned` (breaking)
 - Type `files-matcher` - rename `empty` -> `is-empty` (breaking)
 - Type `file-matcher` - `name` - match base name (also for the GLOB-PATTERN variant) (breaking)
 - Type `file-matcher` - `name` / `path` - Use `~` for regex matching (breaking)
 - Type `string-transformer` - `replace` - Include new-lines in processed lines, unless `-preserve-new-lines` is given (breaking)
 - Type `string-transformer` - `filter`/`LINE-MATCHER` - Optimize by deriving interval of applicable lines
 - Type `string-matcher` - `equals` - Expected value is `STRING-SOURCE`
 - Type `string-matcher` - rename `empty` -> `is-empty` (breaking)
 - Syntax element `STRING-SOURCE` - Option `-file` -> `-contents-of` (breaking)
 - Syntax element `PATH` - Add optional surrounding by parentheses   
 - Syntax element `PATH` - Introduces "reserved words" that must be quoted if used as a file name (breaking)   
 - Syntax element `PROGRAM` - Add optional surrounding by parentheses
 - Interpreter actors - interpreter `EXECUTABLE [ARGUMENT]...` requires `EXECUTABLE` to be a file
 - Actor - `file interpreter` - arguments to source file are `PROGRAM-ARGUMENT`
 - Exit codes - rename `IMPLEMENTATION_ERROR` -> `INTERNAL_ERROR` (breaking)
 - Exit codes - Syntax error in `[act]` - `VALIDATION_ERROR` -> `SYNTAX_ERROR`
 - Exit codes - Values of all non-zero exit codes (breaking)
 - Instruction `conf`/`actor` - Remove "-" prefix from actor names (breaking)
 - Instruction `setup`/`stdin` - Contents value is `STRING-SOURCE`
 - Instruction `assert`/`contents` - Syntax - add `:` between path and matcher (breaking)
 - Instruction `assert`/`dir-contents` - Syntax - add `:` between path and matcher (breaking)
 - Builtin symbol - `string-transformer` - `TO_LOWER_CASE` -> Replaced with `char-case` (breaking)
 - Builtin symbol - `string-transformer` - `TO_UPPER_CASE` -> Replaced with `char-case` (breaking)
 - Builtin symbol - `string-transformer` - `REPLACE_TEST_CASE_DIRS` -> Replaced with `replace-test-case-dirs` (breaking)
 - Builtin symbol - `string` -  `LINE_SEP` -> Rename to `OS_LINE_SEP` (breaking)
 - Syntax of `instruction description` - Delimiter is backtick (`) (breaking)  
 - Phase `conf` - Invalid HDS path gives `VALIDATION_ERROR`

### Removed

 - Interpreter actors - interpreter `$ SHELL-COMMAND`
 - Type `line-matcher` - `matches` - replaced by `contents`

### Fixed

 - Syntax error messages - Include instruction name
 - Help text of instruction `[assert]`/`exists`
 - CLI case:  `--preprocessor` - Detection of invalid argument syntax
 - CLI case:  `--actor`        - Detection of invalid argument syntax
 - CLI suite: `--actor`        - Detection of invalid argument syntax
 - Type `string-transformer` - `replace` - handling of new-lines in replacement string
 - Instruction `assert`/`exists` - Handling of paths with non-last component that is not a directory

## [0.12.3] - 2020-08-18

### Added

 - Builtin symbol - string `LINE_SEP`
 - Builtin symbol - string `TAB`

### Changed

 - Actor `command-line` - Executes a `PROGRAM`

### Fixed

 - Type `files-matcher` / `matches -full` - Crash rendering err msg for recursive model w too few files.
 - Test - tests not working for CWD=/ or CWD=/sub
 - Test - tests not working for Python >= 3.8 (comparison of XML-strings generated from objects with dicts)

## [0.12.2] - 2020-07-21

### Added

 - Type `file-matcher` - primitive `run`
 - Type `string-matcher` - primitive `run`
 - Type `string-transformer` - primitive `run`
 - Instruction `file` - `-ignore-exit-code` option
 - Instruction `run` - `-ignore-exit-code` option

### Fixed

 - Instructions `contents`, `stdout`, `stderr`: Detection of HARD_ERROR from string matcher

## [0.12.1.1] - 2020-06-29

### Added

 - Type `files-condition`
 - Type `files-matcher` - primitive `matches`

### Changed

 - Improves meaning of parentheses in expressions

## [0.12.0] - 2020-02-02

### Added

 - Type `files-matcher` - complex expressions (&& and ||)
 - Type `files-matcher` - `-prune`
 - Type `string-matcher` - complex expressions (&& and ||)
 - Type `file-matcher` - primitive `dir-contents`
 - Type `string-transformer` - primitive `identity`
 - Type `program` - options `-existing-dir`, `-existing-path`
 - Matcher types - primitive `constant`
 - Matcher and `string-transformer` types - alternative syntax for sym-refs: `SYMBOL-REFERENCE`
 - Instruction `dir-contents` - `-recursive` option

### Changed

 - Instruction `def` - LINE-MATCHER argument is mandatory
 - Instruction `def` - FILE-MATCHER argument is mandatory
 - Instruction `def` - STRING-TRANSFORMER argument is mandatory
 - Instruction `def` - PATH argument is mandatory
 - Instruction `env` - Accepts multi line syntax
 - Instruction `dir` - Accepts multi line syntax
 - Instruction `cd` - Accepts multi line syntax
 - Instruction `cd` - PATH argument is mandatory
 - Type `string-transformer` - Rename `select` to `filter`
 - Improved error messages

### Removed

 - The preset `EXACTLY_...` environment variables
 - The "post setup validation" execution step

## [0.11.1.0] - 2019-12-31

### Added

 - Command `symbol` - ability to display information from suite
 - Command `symbol` - ability to display structure of symbols
 - Command `symbol` - ability to handle builtin symbols

### Changed

 - Python compatibility: Increased to Python v 3.5.4
 - Matching on file contents: HARD_ERROR instead of FAIL when file is not an existing regular file
 - Improved error messages

### Fixed

 - Help text of instruction `[conf]`/actor
 
## [0.11.0.1] - 2019-05-02

### Fixed

 - Detection of file inclusion failures in suites
 - suite "progress reporter": Grouping of failing tests
   according to "exit identifier"
 - Help text bug fixes
 - Help text improvements
 - Improvement of some error messages

## [0.11.0] - 2019-03-24

### Changed

 - Instruction `exists`: Replaces file type option with `FILE-MATCHER` 
 
   E.g. `exists -file f.txt` is replaced by `exists f.txt : type file`

## [0.10.0] - 2019-02-05

### Added

 - FILE-MATCHER: New primitive: `contents STRING-MATCHER`
 - FILES-MATCHER: Quantification on files applies `FILE-MATCHER` (instead of `STRING-MATCHER`)
 - STRING-TRANSFORMER: replace: Substitutes symbol references in regex and replacement strings
 - LINE-MATCHER: line-num: Substitutes symbol references in integer comparison

### Changed

 - LINE-MATCHER: Changes name of primitive: "regex" -> "matches"
 - LINE-MATCHER: Substitutes symbol references in regex string
 - FILE-MATCHER: name -regex: Substitutes symbol references in regex string 
 - FILE-MATCHER: name GLOB-PATTERN: Substitutes symbol references in pattern string 

## [0.9.1.1] - 2019-01-26

### Fixed

 - symbol reference reporting: Source location
 - suite parse: Do not crash when parsing suite file with invalid syntax
 
## [0.9.1] - 2019-01-17

### Added

 - New type "string-matcher"
 - New type "files-matcher"
 - New STRING-MATCHER: matches REGEX
 - New command `symbol` - displays information about symbol usages in a test case

### Changed

 - STRING-MATCHER / any|every line: Removes mandatory keyword `matches`

### Fixed

 - Windows - Fixes type error
 - Windows - Avoid crash when resolving terminal ANSI color support
 - Windows - Avoid crash when removing SDS after test case
 
## [0.8.9.5] - 2018-10-06

### Added

 - Test case phase contents in corresponding suites sections
 - Run test case as part of suite if the default suite file - "exactly.suite" - exists
 - Run suites - accepts DIR as suite file CLI arg if DIR contains default suite file
 - Sub suite list accepts DIR if DIR contains default suite file
 - Improved description of Test case execution environment
 - Improved built in help
 - More examples in README
 
### Changed

 - Changes the layout of the sandbox directory structure

### Removed

 - suite/conf instruction `actor`


## [0.8.9.4] - 2018-08-08

### Added

 - def instruction: New path relativity: rel source file: `-rel-here`

### Changed

 - command line     actor: Accepts additional relativities: `-rel-home`, `-rel-act`, `-rel-tmp`
 - file interpreter actor: Accepts additional relativities: `-rel-home`, `-rel-act`, `-rel-tmp`
 - string-transformer "replace": Do not include trailing newline in processed string
 - improves error messages for def instruction - includes source loc of referenced symbols

### Fixed

 - test suites: Environment variables do not leak between test cases


## [0.8.9.2] - 2018-06-24

### Changed

 - `[conf]` instructions: `home`, `act-home`: DIR arg is now relative location of source file
 - `--keep`: Prints sandbox dir also in case of error
 - `--act`: Prints output from ATC continuously, and skips phases `[before-assert]` and `[assert]`
 - Improves built in help (mostly related to "actor", "action to check", "including")
