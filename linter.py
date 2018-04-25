from SublimeLinter.lint import Linter


class phpstan(Linter):
    cmd = 'phpstan analyse --errorFormat raw --no-progress --level max ${file}'
    regex = r'^.*:(?P<line>[0-9]+):(?P<message>.+)'
    default_type = 'error'
    multiline = False
    defaults = {
        'selector': 'source.php'
    }
