SublimeLinter-contrib-phpstan
================================

[![Build Status](https://travis-ci.org/SublimeLinter/SublimeLinter-phpstan.svg?branch=master)](https://travis-ci.org/SublimeLinter/SublimeLinter-phpstan)

This linter plugin for [SublimeLinter](https://github.com/SublimeLinter/SublimeLinter) provides an interface to [phpstan](https://github.com/phpstan/phpstan). This plugin is currently very basic, and pull requests to expand its functionality and configurability are welcome.

## Installation
SublimeLinter must be installed in order to use this plugin.

Please use [Package Control](https://packagecontrol.io) to install the linter plugin.

Before installing this plugin, you must ensure that `phpstan` is installed on your system.

Its suggested to install PHPStan globally with composer.
```
composer global require phpstan/phpstan-shim
```

In order for `phpstan` to be executed by SublimeLinter, you must ensure that its path is available to SublimeLinter. The docs cover [troubleshooting PATH configuration](http://sublimelinter.readthedocs.io/en/latest/troubleshooting.html#finding-a-linter-executable).

## Settings
- SublimeLinter settings: http://sublimelinter.readthedocs.org/en/latest/settings.html
- Linter settings: http://sublimelinter.readthedocs.org/en/latest/linter_settings.html

<!---
Additional SublimeLinter-phpstan settings:

|Setting|Description    |
|:------|:--------------|
|level |The analysis level passed to PHPStan |
--->
