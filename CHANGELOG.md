# ChangeLog


The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

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
