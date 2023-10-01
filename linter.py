import logging
from os import path
from shlex import quote

from SublimeLinter import lint

logger = logging.getLogger('SublimeLinter.plugins.phpstan')


class PhpStan(lint.Linter):
	regex = r'^(?!Note: ).*:(?P<line>[0-9]+):(?P<message>.+)'
	error_stream = lint.STREAM_STDOUT
	# default_type = "error"
	default_type = 'warning'
	multiline = False
	tempfile_suffix = '-'
	defaults = {
		'selector': 'source.php',
		'use_composer_autoload': True,
	}

	def cmd(self):
		command = ['phpstan', 'analyse']
		args = ['--error-format=raw', '--no-progress']

		autoload = self.findAutoload(self.view.file_name())
		if autoload:
			args.append('--autoload-file={}'.format(quote(autoload)))
		return command + args + ['${args}', '${file}']

	def get_cmd(self):
		cmd = self.cmd()
		command = self.build_cmd(cmd) if cmd else []
		return command

	def findAutoload(self, file_path):
		basedir = None
		while file_path:
			basedir = path.dirname(file_path)
			autoload = '{}/vendor/autoload.php'.format(basedir)
			if path.isfile(autoload):
				return 'vendor/autoload.php'
			if basedir == file_path:
				break
			file_path = basedir
