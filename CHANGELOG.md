# Changelog

## [1.12.0](https://github.com/Tugamer89/booklib/compare/v1.11.0...v1.12.0) (2026-05-26)


### Features

* **ui:** improve keyboard accessibility of book search results ([#28](https://github.com/Tugamer89/booklib/issues/28)) ([52be488](https://github.com/Tugamer89/booklib/commit/52be4881e991591d7bf1233026f5aef4f8e06e87))


### Bug Fixes

* **security:** [HIGH] resolve host header injection vulnerability ([#30](https://github.com/Tugamer89/booklib/issues/30)) ([31eecf9](https://github.com/Tugamer89/booklib/commit/31eecf9f313aa79b9552406178566b7b3e0e7eb2))


### Performance Improvements

* add gzip compression middleware to reduce payload size ([#29](https://github.com/Tugamer89/booklib/issues/29)) ([0476a1d](https://github.com/Tugamer89/booklib/commit/0476a1d9d73e93ab653899401b6f7667da49013b))

## [1.11.0](https://github.com/Tugamer89/booklib/compare/v1.10.1...v1.11.0) (2026-05-25)


### Features

* **ui:** add aria-label to ISBN camera scanner button ([#26](https://github.com/Tugamer89/booklib/issues/26)) ([41f78e4](https://github.com/Tugamer89/booklib/commit/41f78e4b795c995a501949a30e22a1177345569d))


### Performance Improvements

* optimize scroll and resize handlers with requestAnimationFrame ([#24](https://github.com/Tugamer89/booklib/issues/24)) ([04899b3](https://github.com/Tugamer89/booklib/commit/04899b378727c63a559376e3215396861522b40b))

## [1.10.1](https://github.com/Tugamer89/booklib/compare/v1.10.0...v1.10.1) (2026-05-24)


### Bug Fixes

* **security:** [CRITICAL] resolve SSRF vulnerability in cover validation ([#22](https://github.com/Tugamer89/booklib/issues/22)) ([a55f49a](https://github.com/Tugamer89/booklib/commit/a55f49a5fb800c56b3b238e08ee2926441618058))
* **ui:** Add aria-label to close buttons in modals ([#21](https://github.com/Tugamer89/booklib/issues/21)) ([2e8fbfb](https://github.com/Tugamer89/booklib/commit/2e8fbfbcfe3410ab01ef093a27af6874df09f999))


### Performance Improvements

* Add database index on frequently queried user_id fields ([#20](https://github.com/Tugamer89/booklib/issues/20)) ([9cc8f32](https://github.com/Tugamer89/booklib/commit/9cc8f32c0b81e09129c6f2fc979ef1edeb56109b))

## [1.10.0](https://github.com/Tugamer89/booklib/compare/v1.9.2...v1.10.0) (2026-05-23)


### Features

* **ui:** Enhance BookCard keyboard accessibility and ARIA labels ([#16](https://github.com/Tugamer89/booklib/issues/16)) ([2fed094](https://github.com/Tugamer89/booklib/commit/2fed09442bb84033fa096cce55b7e553ab7e5eb2))


### Bug Fixes

* **security:** [HIGH] resolve SSRF vulnerability in cover URL validation ([#18](https://github.com/Tugamer89/booklib/issues/18)) ([f13bdf6](https://github.com/Tugamer89/booklib/commit/f13bdf61fc1cd1a6b5684601e8995f4c4e1ec674))


### Performance Improvements

* defer offscreen images loading ([#17](https://github.com/Tugamer89/booklib/issues/17)) ([f13cb7d](https://github.com/Tugamer89/booklib/commit/f13cb7d6ecbc22dfe533b320d50a16951f1da45d))

## [1.9.2](https://github.com/Tugamer89/booklib/compare/v1.9.1...v1.9.2) (2026-05-22)

### Bug Fixes

- pin lucide version to 1.16.0 for stability ([992e18c](https://github.com/Tugamer89/booklib/commit/992e18ce1122f64ea723619069a50cee0591092f))

## [1.9.1](https://github.com/Tugamer89/booklib/compare/v1.9.0...v1.9.1) (2026-05-13)

### Bug Fixes

- rename title from 'Library' to 'BookLib' ([4f714de](https://github.com/Tugamer89/booklib/commit/4f714de8f29061354fe344581290493958aa9aed))

## [1.9.0](https://github.com/Tugamer89/booklib/compare/v1.8.0...v1.9.0) (2026-05-13)

### Features

- translate project content to English ([#8](https://github.com/Tugamer89/booklib/issues/8)) ([862843f](https://github.com/Tugamer89/booklib/commit/862843fd81bd448755c5cdbdadf171b85b07f80f))

## [1.8.0](https://github.com/Tugamer89/booklib/compare/v1.7.0...v1.8.0) (2026-05-09)

### Features

- migrate to Lucide icons and improve UI consistency ([#6](https://github.com/Tugamer89/booklib/issues/6)) ([3a2e366](https://github.com/Tugamer89/booklib/commit/3a2e366a9a7983482f64a6951e8502caa1f95770))

## [1.7.0](https://github.com/Tugamer89/booklib/compare/v1.6.3...v1.7.0) (2026-05-08)

### Features

- Merge pull request [#1](https://github.com/Tugamer89/booklib/issues/1) from Tugamer89/feat/improved-cicd ([2caea3d](https://github.com/Tugamer89/booklib/commit/2caea3d7dd56c08af906c86a24f188882578ddea))

### Bug Fixes

- **ci:** release please extra file type ([dd8e5d2](https://github.com/Tugamer89/booklib/commit/dd8e5d23e0a335cd0559bdee080fa6dc2f79cbe5))
