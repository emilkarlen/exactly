# ChangeLog


The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html),
with exception of a "0." prefix until version 1 is released.

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
 - Improves built in help (mostly related to "actor", ""action to check", "including")
