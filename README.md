# UPDATE PACKAGE VERSION

This package provides a python executable that delivers a path-wide version bump feature.
It reads `~/.update-package-version.yml` file for root paths from which it should start its recursive package search.

Package versions are updated using these glob patterns by default:
 - `**/Pipfile`
 - `**/requirements.txt`
 - `requirements/**.txt`


## Installation

```bash
pip install update-package-version
```    

## Usage

```bash
./upv.py -- --help

# upv.py [CONFIG_FILE_PATH] [CONFIG_FILE_NAME] [CWD]
# upv.py [--config-file-path CONFIG_FILE_PATH] [--config-file-name CONFIG_FILE_NAME] [--cwd CWD]

```

```bash
# You can use update-package-version command
# or upv shortcut
upv find package-name --src 0.0.1
upv find package-name
upv update package-name --src 0.0.1 --trg 1.1.1

# Assumes src == *
upv update package-name --trg 1.1.1

```

## Configuration

```yaml
######################################
# CONVENIENCE PYTHON PACKAGE ALIASES #
######################################
.RE:
    # matches `sample-package` and `sample-package==0.0.1`
    .package: &include-package '(?P<package>{package})(?P<sign>\=\=|\<\=|\>\=|\<|\>)?(?P<version>[\-\d\.]+)?'

    # matches `sample-package.git@0.0.1`
    .git-package: &include-git-package '(?P<package>{package})\.git@(?P<version>[\-\d\.]+)'

    .EXCLUDE:
        # matches all the lines start with the hash character
        .comment: &no-comment '^\s*#.+'

        # just aliasing `*include-git-package` to make it more readable across the config file
        .git-package: &no-git-package '(?P<package>{package})\.git@(?P<version>[\-\d\.]+)'

########################################
# SOME USEFUL PYTHON PATTERN TEMPLATES #
########################################
.GENERIC-PATTERNS:
    # use these lines along with something like `pattern: '**/requirements.txt'`
    .generic-requirements-package: &generic-requirements-package
        replacer: RegexReplacer
        # AND logic is used here
        include-patterns: []
        # OR logic is used here
        match-patterns:
            - *include-package
        # OR logic is used here
        exclude-patterns:
            - *no-git-package
            - *no-comment

    .git-repo-requirements-package: &git-repo-requirements-package
        replacer: RegexReplacer
        match-patterns:
            - *include-git-package
        exclude-patterns:
            - *no-comment

defaults:
  file-patterns: &default-file-patterns
    # Generic Pipfile parser
    - pattern: '**/Pipfile'
      replacer: PipfileReplacer

    # an utterly broad glob pattern for everything that looks like a python package file,
    # but NOT a .git repo
    - pattern: '**/requirements.txt'
      <<: *generic-requirements-package

    # and this one for .git repo ONLY
    - pattern: '**/requirements.txt'
      <<: *git-repo-requirements-package

    # ... when you love segmentation too much
    - pattern: '**/requirements/*.txt'
      <<: *generic-requirements-package

    - pattern: '**/requirements/*.txt'
      <<: *git-repo-requirements-package

origins:
  - root: '/tmp/sample-project-group'
    file-patterns: *default-file-patterns
    on-update:
      - echo LOL LOL LOL
      - echo COOL COOL COOL

```