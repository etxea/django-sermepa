# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.1] - 2026-04-13

### Fixed

- Merchant parameters are now converted to strings before JSON encoding (Redsys requires all values as strings)
- Updated test view to use `merchant_parameters` kwarg instead of `initial`

## [2.0.0] - 2026-04-11

### Added

- Support for Django 3.2, 4.0, 4.1, 4.2, 5.0, 5.1
- Support for Python 3.8 - 3.13
- `pyproject.toml` for modern Python packaging
- GitHub Actions CI testing across all supported Django/Python combinations
- GitHub Actions workflow for automated PyPI publishing on release
- `tox` configuration for local multi-version testing
- `CHANGELOG.md`
- Expanded test suite with tests for mixins, forms, signals, and IPN view

### Changed

- Replaced `django.conf.urls.url()` with `django.urls.path()`
- Replaced `django.conf.urls.patterns()` with plain list `urlpatterns`
- Replaced `django.core.urlresolvers` imports with `django.urls`
- Replaced `MIDDLEWARE_CLASSES` with `MIDDLEWARE` in settings
- Replaced `TEMPLATE_LOADERS`/`TEMPLATE_DIRS` with `TEMPLATES` setting
- Replaced `render_to_response` with `render`
- Replaced `execute_manager` with `execute_from_command_line` in manage.py
- Replaced `__unicode__` with `__str__` on models
- Added `DEFAULT_AUTO_FIELD` setting
- Updated `pyDes` IV/pad to use bytes instead of strings
- Bumped version to 2.0.0

### Removed

- Support for Django < 3.2
- Support for Python < 3.8
- `from __future__ import unicode_literals` (Python 3 only)
- Debug `print()` statement in forms

## [1.1.5] - Previous release

### Fixed

- Bug fixes in form and mixin
- Tested on Django 2.2 and Python 3.8
