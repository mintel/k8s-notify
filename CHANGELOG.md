# Changelog
All notable changes to this project will be documented in this file.

## v0.2.0 (2021-50-13)
### Changed
- Bump base image to `python:3.9-slim-buster`
- Bump all package versions
- Update example deployment to use latest Kubernetes API

### Fixed
- Remove trailing whitespace from `CMD` value when referencing `config.yml`

## v0.1.1 (2020-04-20)
### Fixed
- Take into account unavailable-replicas when setting rollout-complete status

## v0.1.0 (2020-04-20)
- Initial release
