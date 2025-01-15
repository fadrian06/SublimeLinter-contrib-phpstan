import json
import logging
import re
from os import path

from SublimeLinter import lint
from SublimeLinter.lint import ComposerLinter

logger = logging.getLogger("SublimeLinter.plugins.phpstan")


class PhpStan(ComposerLinter):
    defaults = {
        "selector": "embedding.php, source.php"
    }

    def cmd(self) -> str:
        cmd = "phpstan analyze ${file} --error-format=json --no-progress ${args}"
        cwd = self.get_working_dir()

        config_file_paths = (
            f"{cwd}{path.sep}phpstan.neon",
            f"{cwd}{path.sep}phpstan.neon.dist"
        )

        for config_file_path in config_file_paths:
            if path.exists(config_file_path):
                cmd += " -c phpstan.neon"

        return cmd

    def find_errors(self, output: str):
        try:
            content = json.loads(output)
        except ValueError:
            logger.error(
                "JSON Decode error: We expected JSON from PHPStan, "
                "but instead got this:\n{}\n\n"
                .format(output)
            )
            self.notify_failure()
            return

        if 'files' not in content:
            return

        for file in content['files']:
            for error in content['files'][file]['messages']:
                error_message = error['message']

                if 'tip' in error:
                    # the character • is used for list in tips
                    tip = error['tip'].replace("•", "💡")

                    if not tip.startswith("💡"):
                        tip = "💡 " + tip

                    error_message = error_message + "\n" + tip

                line_region = self.view.line(
                    self.view.text_point(error['line'] - 1, 0))
                line_content = self.view.substr(line_region)

                stripped_line = line_content.lstrip()
                leading_whitespace_length = len(
                    line_content) - len(stripped_line)

                # Highlight the whole line by default
                key = self.extract_offset_key(error)
                col = leading_whitespace_length
                end_col = len(line_content)

                if key:
                    pattern = rf"{key}"
                    # Check if key begins with $
                    if key.startswith('$'):
                        pattern = rf"\{key}"

                    key_match = re.search(pattern, line_content)

                    if key_match:
                        # Compute the start and end columns
                        col = key_match.start()
                        end_col = key_match.end()

                yield lint.LintMatch(
                    match=error,
                    filename=file,
                    line=error['line'] - 1,
                    col=col,
                    end_col=end_col,
                    message=error_message,
                    error_type='error',
                    code='',
                )

    def extract_offset_key(self, error: dict):
        error_message = error.get('message', '')

        if 'identifier' not in error:
            return None

        patterns = {
            'offsetAccess.notFound': r"Offset '([^']+)'",
            'argument.type': [
                r'Parameter #\d+ \$(\w+) of method [\w\\]+::(\w+)\(\) expects .*, .+ given\.',
                r'function (\w+)',
                r'Method ([\w\\]+)::(\w+)\(\) is unused\.'
            ],
            'arguments.count': [
                r'Method [\w\\]+::(\w+)\(\) invoked with \d+ parameters, \d+ required\.',
                r'Static method (\w+::\w+)\(\) invoked with \d+ parameter'
            ],
            'property.onlyWritten': r'Property [\w\\]+::(\$\w+) is never read, only written\.',
            'property.unused': [
                r'Property [\w\\]+::(\$\w+) is unused\.',
                r'Static property ([\w\\]+)::(\$\w+) is unused\.'
            ],
            'property.notFound': r'Access to an undefined property [\w\\]+::\$(\w+)\.',
            'property.nonObject': r'property \$([\w_]+) on mixed\.',
            'missingType.return': r'Method ([\w\\]+)::(\w+)\(\) has no return type specified\.',
            'missingType.iterableValue': r'Method [\w\\]+::\w+\(\) has parameter (\$\w+) with no value type specified in iterable type array\.',
            'missingType.property': r'Property [\w\\]+::(\$\w+) has no type specified\.',
            'missingType.parameter': r'Method [\w\\]+::\w+\(\) has parameter (\$\w+) with no type specified\.',
            'method.unused': r'Method ([\w\\]+)::(\w+)\(\) is unused\.',
            'method.notFound': r'Call to an undefined method [\w\\]+::(\w+)\(\)\.',
            'constructor.unusedParameter': r'Constructor of class [\w\\]+ has an unused parameter (\$\w+)\.',
            'class.notFound': [
                r'on an unknown class [\w\\]+\\(\w+)\.',
                r'has unknown class [\w\\]+\\(\w+) as its type\.',
                r'Instantiated class [\w\\]+\\(\w+) not found\.',
                r'Parameter \$\w+ of method [\w\\]+::\w+\(\) has invalid type (\w+)\.',
                r'Call to method (\w+)\(\) on an unknown class (\w+)\.',
                r'Method [\w\\]+::\w+\(\) has invalid return type (\w+)\.',
                r'extends unknown class [\w\\]+\\(\w+)\.'
            ],
            'classConstant.notFound': r'(::\w+)\.',
            'assign.propertyReadOnly': r'Property object\{[^}]*\bname: string\b[^}]*\}::\$(\w+) is not writable\.',
            'assign.propertyType': r'does not accept [\w\\]+\\(\w+)\.',
            'constant.notFound': r'Constant (\w+) not found\.',
            'function.nameCase': r'incorrect case: (\w+)',
            'function.notFound': r'Function (\w+) not found\.',
            'function.strict': r'Call to function (\w+)\(\)',
            'staticMethod.notFound': r'undefined static method (\w+::\w+)\(\)\.',
            'staticMethod.void': r'static method [\w\\]+::(\w+)\(\)',
            'variable.undefined': [
                r'Undefined variable: (\$\w+)',
                r'Variable (\$\w+) might not be defined\.'
            ],
            'interface.notFound': r'implements unknown interface [\w\\]+\\(\w+)\.',
            'isset.offset': r'Offset \'(\w+)\' on array',
            'staticProperty.notFound': r'static property [\w\\]+::(\$\w+)',
            'return.phpDocType': r'native type (\w+)'
        }

        identifier = error['identifier']

        if identifier in patterns:
            pattern = patterns[identifier]

            if isinstance(pattern, list):
                for pat in pattern:
                    match = re.search(pat, error_message)

                    if match:
                        return match.group(1)
            else:
                match = re.search(pattern, error_message)

                if match:
                    return match.group(1)

        return None
