# Changelog

## [1.16.2](https://github.com/Tugamer89/booklib/compare/v1.16.1...v1.16.2) (2026-06-04)


### Performance Improvements

* optimize books-data serialization ([#67](https://github.com/Tugamer89/booklib/issues/67)) ([2aa8d3d](https://github.com/Tugamer89/booklib/commit/2aa8d3df2afdd906184127cec1ed477443eb4cd4))

## [1.16.1](https://github.com/Tugamer89/booklib/compare/v1.16.0...v1.16.1) (2026-06-04)


### Bug Fixes

* **security:** [MEDIUM] restrict sort_by to allowed columns to prevent DoS via unhandled ORM exceptions ([#65](https://github.com/Tugamer89/booklib/issues/65)) ([f813547](https://github.com/Tugamer89/booklib/commit/f8135474e42ca8e750e4d1c90e92febf4db1efdf))

## [1.16.0](https://github.com/Tugamer89/booklib/compare/v1.15.0...v1.16.0) (2026-06-03)


### Features

* **ui:** improve empty state with helpful call-to-action ([#61](https://github.com/Tugamer89/booklib/issues/61)) ([12f77e5](https://github.com/Tugamer89/booklib/commit/12f77e5fd13042f9bf9dcf755900fb550b74a829))


### Bug Fixes

* **security:** [HIGH] resolve open redirect vulnerability in redirect URL validation ([#62](https://github.com/Tugamer89/booklib/issues/62)) ([5077321](https://github.com/Tugamer89/booklib/commit/5077321472eafbbcb817f39aef8eef79d81014d2))


### Performance Improvements

* lazy load html5-qrcode library ([#63](https://github.com/Tugamer89/booklib/issues/63)) ([b513968](https://github.com/Tugamer89/booklib/commit/b5139686a6a8771033d72901d482cea9bbbe995a))

## [1.15.0](https://github.com/Tugamer89/booklib/compare/v1.14.0...v1.15.0) (2026-06-02)


### Features

* **ui:** add loading state to save book form submission ([#58](https://github.com/Tugamer89/booklib/issues/58)) ([3107e6a](https://github.com/Tugamer89/booklib/commit/3107e6adbd0e863ba30a6dbb4de3f7bc1dedc611))


### Bug Fixes

* **security:** [CRITICAL] resolve SSRF vulnerability in cover URL validation ([#59](https://github.com/Tugamer89/booklib/issues/59)) ([39cf6ec](https://github.com/Tugamer89/booklib/commit/39cf6eccf12c69cf286eea1e2e2f65095a4ee250))

## [1.14.0](https://github.com/Tugamer89/booklib/compare/v1.13.1...v1.14.0) (2026-06-01)


### Features

* admin ux and security improvements ([#53](https://github.com/Tugamer89/booklib/issues/53)) ([76ad1a7](https://github.com/Tugamer89/booklib/commit/76ad1a797c8a9ec2b5d702a2f5ac24a988005f90))
* **ui:** add colored required indicators to form fields ([#50](https://github.com/Tugamer89/booklib/issues/50)) ([38117d7](https://github.com/Tugamer89/booklib/commit/38117d71697da73aa87d29ca37ac89e9d44e7549))
* **ui:** add focus visible styles for keyboard navigation ([#57](https://github.com/Tugamer89/booklib/issues/57)) ([8f4b0b2](https://github.com/Tugamer89/booklib/commit/8f4b0b2f5b328b8d72a5112de022c374e91ae851))


### Bug Fixes

* **security:** [HIGH] resolve missing rate limiting on auth and admin endpoints ([#56](https://github.com/Tugamer89/booklib/issues/56)) ([96d9a03](https://github.com/Tugamer89/booklib/commit/96d9a03da9df8f61ff761425035d0fc2a068d406))
* **security:** resolve missing rate limiting on auth and admin endpoints ([96d9a03](https://github.com/Tugamer89/booklib/commit/96d9a03da9df8f61ff761425035d0fc2a068d406))


### Performance Improvements

* offload synchronous email sending to threadpool ([#55](https://github.com/Tugamer89/booklib/issues/55)) ([7d1cd67](https://github.com/Tugamer89/booklib/commit/7d1cd67fa338a7e8df424cf0d03f412153295a9e))
* throttle modal scroll events ([#52](https://github.com/Tugamer89/booklib/issues/52)) ([39756e4](https://github.com/Tugamer89/booklib/commit/39756e4cd4262ac7bf6e976f98a30b4375207f05))

## [1.13.1](https://github.com/Tugamer89/booklib/compare/v1.13.0...v1.13.1) (2026-05-30)


### Bug Fixes

* **security:** [HIGH] resolve SSRF and Open Redirect / XSS vulnerabilities ([#48](https://github.com/Tugamer89/booklib/issues/48)) ([f94873d](https://github.com/Tugamer89/booklib/commit/f94873d75687c2496034d3093cd01b210d307149))

## [1.13.0](https://github.com/Tugamer89/booklib/compare/v1.12.3...v1.13.0) (2026-05-30)


### Features

* **ui:** improve auth tabs accessibility ([#45](https://github.com/Tugamer89/booklib/issues/45)) ([b81b555](https://github.com/Tugamer89/booklib/commit/b81b5558bf3eb667af1c93276053ef10a0ebd26d))


### Bug Fixes

* add missing token parameter for GitHub Actions checkout step ([59630cb](https://github.com/Tugamer89/booklib/commit/59630cb32e590875ff3efc96a820e78e9706a690))
* update dependencies and version to 1.12.3; enhance security headers and improve README formatting ([03812f5](https://github.com/Tugamer89/booklib/commit/03812f536f2ddbad31f5d30771c7a89a4f393d73))


### Performance Improvements

* Offload synchronous blocking image I/O to threadpool ([#47](https://github.com/Tugamer89/booklib/issues/47)) ([28c9e70](https://github.com/Tugamer89/booklib/commit/28c9e705ab24b19a7c1a82fd005d01654c2000da))

## [1.12.3](https://github.com/Tugamer89/booklib/compare/v1.12.2...v1.12.3) (2026-05-29)

### Bug Fixes

- Add lint-and-format-bypass for bot triggers ([#42](https://github.com/Tugamer89/booklib/issues/42)) ([9869a3c](https://github.com/Tugamer89/booklib/commit/9869a3cd820ac1117b97d375a69c4272f9a5eff9))
- modify CSP to enhance security and resource loading ([#44](https://github.com/Tugamer89/booklib/issues/44)) ([8847d58](https://github.com/Tugamer89/booklib/commit/8847d583d4cdb1c85910a66d01a993399c10724f))
- **security:** add HTTP security headers middleware ([#38](https://github.com/Tugamer89/booklib/issues/38)) ([0e32826](https://github.com/Tugamer89/booklib/commit/0e32826bd8048ac74bc7eb5332504c81fd2b400e))
- **ui:** improve keyboard accessibility for cover upload input ([#39](https://github.com/Tugamer89/booklib/issues/39)) ([90f6e90](https://github.com/Tugamer89/booklib/commit/90f6e90160b3c33007fec4abf6a0b8ec371ddcf8))
- Update Content Security Policy in middleware.py ([#41](https://github.com/Tugamer89/booklib/issues/41)) ([268e960](https://github.com/Tugamer89/booklib/commit/268e96042fe7ec7b668550da22da065c6c25acf8))

### Performance Improvements

- Cache Google Books API searches and handle quota errors ([#43](https://github.com/Tugamer89/booklib/issues/43)) ([6f8cfec](https://github.com/Tugamer89/booklib/commit/6f8cfec58f157d063f61228ddc0fba2128f1daba))

## [1.12.2](https://github.com/Tugamer89/booklib/compare/v1.12.1...v1.12.2) (2026-05-28)

### Bug Fixes

- **security:** resolve open redirect vulnerability ([#35](https://github.com/Tugamer89/booklib/issues/35)) ([0342091](https://github.com/Tugamer89/booklib/commit/0342091e6c60a23429c80238123be633bfd29152))

### Performance Improvements

- optimize books list database query ([#36](https://github.com/Tugamer89/booklib/issues/36)) ([91853f8](https://github.com/Tugamer89/booklib/commit/91853f843cb7188095758c77fd640d14b5a05e35))

## [1.12.1](https://github.com/Tugamer89/booklib/compare/v1.12.0...v1.12.1) (2026-05-27)

### Performance Improvements

- optimize get_authenticated_user query with joinedload ([#32](https://github.com/Tugamer89/booklib/issues/32)) ([a08ef4f](https://github.com/Tugamer89/booklib/commit/a08ef4f7b05cd65dc9b341bf8af455fe30470c05))

## [1.12.0](https://github.com/Tugamer89/booklib/compare/v1.11.0...v1.12.0) (2026-05-26)

### Features

- **ui:** improve keyboard accessibility of book search results ([#28](https://github.com/Tugamer89/booklib/issues/28)) ([52be488](https://github.com/Tugamer89/booklib/commit/52be4881e991591d7bf1233026f5aef4f8e06e87))

### Bug Fixes

- **security:** [HIGH] resolve host header injection vulnerability ([#30](https://github.com/Tugamer89/booklib/issues/30)) ([31eecf9](https://github.com/Tugamer89/booklib/commit/31eecf9f313aa79b9552406178566b7b3e0e7eb2))

### Performance Improvements

- add gzip compression middleware to reduce payload size ([#29](https://github.com/Tugamer89/booklib/issues/29)) ([0476a1d](https://github.com/Tugamer89/booklib/commit/0476a1d9d73e93ab653899401b6f7667da49013b))

## [1.11.0](https://github.com/Tugamer89/booklib/compare/v1.10.1...v1.11.0) (2026-05-25)

### Features

- **ui:** add aria-label to ISBN camera scanner button ([#26](https://github.com/Tugamer89/booklib/issues/26)) ([41f78e4](https://github.com/Tugamer89/booklib/commit/41f78e4b795c995a501949a30e22a1177345569d))

### Performance Improvements

- optimize scroll and resize handlers with requestAnimationFrame ([#24](https://github.com/Tugamer89/booklib/issues/24)) ([04899b3](https://github.com/Tugamer89/booklib/commit/04899b378727c63a559376e3215396861522b40b))

## [1.10.1](https://github.com/Tugamer89/booklib/compare/v1.10.0...v1.10.1) (2026-05-24)

### Bug Fixes

- **security:** [CRITICAL] resolve SSRF vulnerability in cover validation ([#22](https://github.com/Tugamer89/booklib/issues/22)) ([a55f49a](https://github.com/Tugamer89/booklib/commit/a55f49a5fb800c56b3b238e08ee2926441618058))
- **ui:** Add aria-label to close buttons in modals ([#21](https://github.com/Tugamer89/booklib/issues/21)) ([2e8fbfb](https://github.com/Tugamer89/booklib/commit/2e8fbfbcfe3410ab01ef093a27af6874df09f999))

### Performance Improvements

- Add database index on frequently queried user_id fields ([#20](https://github.com/Tugamer89/booklib/issues/20)) ([9cc8f32](https://github.com/Tugamer89/booklib/commit/9cc8f32c0b81e09129c6f2fc979ef1edeb56109b))

## [1.10.0](https://github.com/Tugamer89/booklib/compare/v1.9.2...v1.10.0) (2026-05-23)

### Features

- **ui:** Enhance BookCard keyboard accessibility and ARIA labels ([#16](https://github.com/Tugamer89/booklib/issues/16)) ([2fed094](https://github.com/Tugamer89/booklib/commit/2fed09442bb84033fa096cce55b7e553ab7e5eb2))

### Bug Fixes

- **security:** [HIGH] resolve SSRF vulnerability in cover URL validation ([#18](https://github.com/Tugamer89/booklib/issues/18)) ([f13bdf6](https://github.com/Tugamer89/booklib/commit/f13bdf61fc1cd1a6b5684601e8995f4c4e1ec674))

### Performance Improvements

- defer offscreen images loading ([#17](https://github.com/Tugamer89/booklib/issues/17)) ([f13cb7d](https://github.com/Tugamer89/booklib/commit/f13cb7d6ecbc22dfe533b320d50a16951f1da45d))

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
