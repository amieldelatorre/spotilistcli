# Changelog

## [0.0.7] - 2024-03-xx

### Added
- Import exit from sys
- Add instructions on how to build
- Makefile for cleaning, setting up environment and building
- Create executables for windows amd64 and linux amd64 when pushing tag
- Separate function for getting the cache file path
- Decorator function for checking if the user is logged in

### Fixed
N/A

### Changed
- Changed how the working directory is set based on the `SPOTILISTCLI_ENVIRONMENT` environment variable
  - It will be the path of the executable when set to `production`
  - OR it will be the path of the app.py file when set to anything else
- Wrapping the auth logout command with the check logged in decorator function

### Removed
N/A


[0.0.7]: https://github.com/amieldelatorre/spotilistcli/compare/0.0.6...0.0.7