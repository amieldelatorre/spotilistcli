# Changelog

## [0.3.2] - 2024-05-25

### Added
- Added Owner Spotify Id to fields in playlists export
- Added a filter for owned playlists
  - `--filter-owned`: Grabs playlists that are owned
- Filters will be evaluated as OR
- Add an overwrite option when validating Youtube URLs
- Include None or empty Youtube URLs when validating but force overwrite
 
### Fixed
- Handle the end of the list when validating Youtube URLs

### Changed
N/A

### Removed
N/A


[0.3.2]: https://github.com/amieldelatorre/spotilistcli/compare/0.3.1...0.3.2