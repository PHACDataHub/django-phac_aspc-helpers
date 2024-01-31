# Changelog

## [1.3.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.2.0...v1.3.0) (2024-01-31)

### Features

- add ability to use non-queryset iterators in excel/csv export utils ([#84](https://github.com/PHACDataHub/django-phac_aspc-helpers/pull/84))
- fix csv name issue ([#85](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/85)) ([8738958](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/873895841a2712e7e3d2710a0100842c15f382b0))

## [1.2.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.1.1...v1.2.0) (2023-10-25)

### Features

- add csv export utils ([#70](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/70)) ([e9fb3e5](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/e9fb3e5308a2be64c9dcf7243b9f47c506e87132))
- add rules utility ([#74](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/74)) ([322f5a2](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/322f5a2ed7ac142df7e40d447794e4602fabb430))

## [1.1.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.1.0...v1.1.1) (2023-10-03)

### Miscellaneous Chores

- release 1.1.1 ([b7562b2](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/b7562b2a7f80bbd88e9456aa1ce1c336eae29667))

## [1.1.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.6...v1.1.0) (2023-10-03)

### Features

- templatetag for inlining the content of an svg from an app's static files in to a template ([#59](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/59)) ([238799d](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/238799dbf72022fa3ca5b61bba46724cdcc2665d))

## [1.0.6](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.5...v1.0.6) (2023-09-27)

### Bug Fixes

- Fixes session timeout dialog accuracy ([2cc4038](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/2cc403898bebae29549692fcfe24ab2ff0258ca1)), closes [#53](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/53)

## [1.0.5](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.4...v1.0.5) (2023-09-26)

### Bug Fixes

- for real, final fix to the slack logging filter code. Another dumb code typo that slipped through ([1cf4c11](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/1cf4c11f8f27864def1ac95ade8215eada918f11))

## [1.0.4](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.3...v1.0.4) (2023-09-26)

### Bug Fixes

- ... second hotfix for the slack logging webhook's noisy logger filter, I forgot to convert it to the correct class syntax when I refactored additional_filter_configs pattern. I'll follow up with a proper PR to make sure the tests actually cover this ([d931cb1](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/d931cb13b719a2e2a22458376b4ccb7cd6f1857e))

## [1.0.3](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.2...v1.0.3) (2023-09-26)

### Features

- PHAC logo SVGs ([#48](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/48)) ([2bcc37f](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/2bcc37fd1d3ffadcce33a8636b7112463cb40beb))

### Bug Fixes

- fix typo in the default logging config, only reachable when a slack webhook url is provided ([2ef56b1](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/2ef56b1d8f9ba1dadbb9e84478c100ae6d2cede2))

## [1.0.2](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.1...v1.0.2) (2023-09-26)

### Features

- logging utilities and (opt-in) default logging configuration ([#38](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/38)) ([1776952](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/1776952abb8ac274196263e8c2ef927051bc4e0a))

## [1.0.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v1.0.0...v1.0.1) (2023-09-20)

### Features

- DTL template tag and Jinja2 util func for rendering a template from one language inside another ([#43](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/43)) ([8bde55f](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/8bde55f544e11e6e80bcbd7f0aed9d210e130017))

## [1.0.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.7.0...v1.0.0) (2023-09-19)

### ⚠ BREAKING CHANGES

- **deps:** Drop python 3.8 and 3.9 support, unify github action jobs ([#44](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/44))

### Miscellaneous Chores

- **deps:** Drop python 3.8 and 3.9 support, unify github action jobs ([#44](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/44)) ([1874608](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/18746087532ce48779d1791c5fcfa55d013ea0de))

## [0.7.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.6.0...v0.7.0) (2023-08-31)

### Features

- add more utils (excel, vanilla python stuff, custom model fields) ([#33](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/33)) ([8433a60](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/8433a603d6a78a7a9c208b7d88eb031060038228))

## [0.6.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.5.1...v0.6.0) (2023-07-11)

### Features

- support URL query params (including 'next' redirect) ([#25](https://github.com/PHACDataHub/django-phac_aspc-helpers/issues/25)) ([8c99399](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/8c99399bcf0a26a4c40ceb68c93b84e0a91c5451))

## [0.5.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.5.0...v0.5.1) (2023-06-16)

### Bug Fixes

- Include translation files in release ([37e165d](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/37e165d048e64526258dcfe340dd23f319a9db98))

## [0.5.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.4.4...v0.5.0) (2023-06-08)

### Features

- Added support to sign in using the Microsoft Identity Platform ([c430b5f](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/c430b5f26e75e603dad149276c5af387ac9d9a51))

## [0.4.4](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.4.3...v0.4.4) (2023-03-06)

### Bug Fixes

- Ensure .env file from root of project dir is read by django-environ ([05dc452](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/05dc4526b34f6dea5e03ec8ebd6fb3f21754e68f))

## [0.4.3](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.4.2...v0.4.3) (2023-02-22)

### Bug Fixes

- Removed tests from templatetags directory ([c801855](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/c801855c779b1f10b5175c8baf2f57df8d894460))

## [0.4.2](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.4.1...v0.4.2) (2023-02-10)

### Bug Fixes

- Added utility to alter settings during unit tests ([540228f](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/540228ffed72d44095a8e7776b1b164a7d2f92b8))

## [0.4.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.4.0...v0.4.1) (2023-02-09)

### Bug Fixes

- Updated incorrect django version dependency ([82f1218](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/82f1218f9aeefdd8bf345a68cfe32e78806a9c6f))

## [0.4.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.3.1...v0.4.0) (2023-01-10)

### Features

- AC-7: Implemented account lockout controls ([c5f07ef](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/c5f07efb554181f9cb81716f8861b61901afca56))

## [0.3.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.3.0...v0.3.1) (2023-01-09)

### Documentation

- Updated import statement in readme file ([76d6856](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/76d685679a055f380e290c408c4e13f3d46dd67e))

## [0.3.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.2.1...v0.3.0) (2023-01-06)

### Features

- Environment variable support ([8383e8b](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/8383e8b62556f31658f0309be7ab699bab23ca05))

## [0.2.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.2.0...v0.2.1) (2022-12-22)

### Bug Fixes

- Namespaced base css to avoid conflicts with bootstrap ([d6fc06f](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/d6fc06fe97389723813c69a9065fe5454e340980))
- removed dependency on jQuery which can cause errors ([ad53b35](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/ad53b355955be6cee6a1a2d801146b68eeb80fb1))

## [0.2.0](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.1.1...v0.2.0) (2022-12-21)

### Features

- Replaced built in WET with CDN hosted version ([74e6b77](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/74e6b7765c02afac478b488f70f7063fe4ad35b9))

## [0.1.1](https://github.com/PHACDataHub/django-phac_aspc-helpers/compare/v0.1.0...v0.1.1) (2022-12-20)

### Bug Fixes

- Update packaging config to include all required files ([43ad20d](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/43ad20d2432bc3eb825af98269e613f098543fc2))

## 0.1.0 (2022-12-20)

### Features

- **security:** Session Timeouts (AC-11) ([84f08ec](https://github.com/PHACDataHub/django-phac_aspc-helpers/commit/84f08eccdb312d4b0d2be5df6b864de86539041b))
