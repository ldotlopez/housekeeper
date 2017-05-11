from housekeeper import pluginlib

import copy
import functools
import re


# /music -> main endpoint
# /music/play (what=str, type=[playlist|artist|album|query]) -> Play something
# /music/search (q=str)

# pluginlib.method llama previamente al metodo validador de la clase correspondiente


def method(fn):
	return fn


class Parameter:
	def __init__(self, name, abbr=None, **kwargs):
		if not re.match(r'^[a-z0-9-_]+$', name, re.IGNORECASE):
			raise ValueError(name)

		if abbr and len(abbr) != 1:
			msg = "abbr must be a single letter"
			raise ValueError(abbr, msg)

		self.name = str(name).replace('-', '_')
		self.abbr = str(abbr) if abbr else None
		self.kwargs = copy.copy(kwargs)

	@property
	def short_flag(self):
		if not self.abbr:
			return None

		return '-' + self.abbr

	@property
	def long_flag(self):
		return '--' + self.name.replace('_', '-')


class Method(pluginlib.Command):
	PARAMETERS = ()

	def __init__(self, *args, **kwargs):
		pass

	def setup_argparser(self, parser):
		for param in self.PARAMETERS:
			fn = parser.add_argument

			if param.short_flag:
				fn = functools.partial(fn, param.short_flag)

			fn = functools.partial(fn, param.long_flag)
			fn(**param.kwargs)

	def execute(self, core, arguments):
		parameters = {}
		for param in self.PARAMETERS:
			try:
				parameters[param.name] = getattr(arguments, param.name)
			except AttributeError:
				pass

		return self.main(**parameters)

	def main(self, **paramters):
		raise NotImplementedError()


class Applet(Method):
	def __init__(self, *args, **kwargs):
		self.methods = {}
		for (name, methodcls) in self.METHODS:
			method = methodcls(*args, **kwargs)
			self.methods[name] = method

	def setup_argparser(self, parser):
		# Add subparsers for methods
		if self.methods:
			subparsers = parser.add_subparsers(dest='method')

			for (name, method) in self.methods.items():
				method_parser = subparsers.add_parser(name)
				method.setup_argparser(method_parser)

		super().setup_argparser(parser)


	def execute(self, core, arguments):
		method = arguments.method
		if method:
			return self.methods[method].execute(core, arguments)

		return super().execute(core, arguments)


class MusicPlay(Method): 
	"""
	/music/play

	what: What to play (some playlist, artist, album, etc...)
	type: Specify `what` type (optional)
	"""
	PARAMETERS = (
		Parameter('what', type=str, required=True),
		Parameter('type', abbr='t', type=str)
	)

	@method
	def main(self, **kwargs):
		# Call /usr/bin/media-player play 'what'
		print(repr(kwargs))

	def validator(self, **kwargs):
		# Validate kwargs
		return kwargs


class MusicStop(Method):
	@method
	def main(self, **kwargs):
		# Call /usr/bin/media-player stop
		pass


class MusicPause(Method):
	@method
	def main(self, **kwargs):
		# Call /usr/bin/media-player stop
		pass


class Music(Applet):
	"""/music"""
	__extension_name__ = 'music'

	HELP = 'Music control'
	PARAMETERS = (
		Parameter('foo', required=False),
	)

	METHODS = (
		('play', MusicPlay),
		('pause', MusicPause),
		('stop', MusicStop),
	)


	def main(self, foo):
		print('Hi! (foo={})'.format(foo))


__housekeeper_extensions__ = [
	Music
]
