# ChangeLog


The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Changed

 - command line actor: Accepts additional relativities HOME/case, SANDBOX/act, SANDBOX/tmp
 - file interpreter actor: Accepts additional relativities HOME/case, SANDBOX/act, SANDBOX/tmp
 - string-transformer "replace": Do not include trailing newline in processed string


## [0.8.9.2] - 2018-06-24

### Changed

 - `[conf]` instructions: `home`, `act-home`: DIR arg is now relative location of source file
 - `--keep`: Prints sandbox dir also in case of error
 - `--act`: Prints output from ATC continuously, and skips phases `[before-assert]` and `[assert]`
 - Improves built in help (mostly related to "actor", ""action to check", "including")
