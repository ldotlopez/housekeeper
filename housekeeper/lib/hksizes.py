from humanfriendly import parse_size

__all__ = [
	'parse_size'
]

# import re
# _SIZE_SUFFIXES = 'k m g t p e z y'.split()


# def _parse_size(s):
# 	s_ = str(s)
# 	s_ = s_.replace(' ', '').lower()

# 	import ipdb; ipdb.set_trace(); pass
# 	# m = re.search(r'^(?P<amount>[0-9]+(([\.,]+)(?P<decimal>[0-9]+)?)?)(?P<suffix>b|da|h|k|g|t|p|e)(?P<BIN>i)?', s_)
# 	m = re.search(r'(?P<amount>[0-9,.]+)(?P<qual>ki?|gi?|ti?|pi?|ei?)?', s_)
# 	if not m:
# 		raise ValueError(s)
	
# 	groups = m.groupdict()

# 	# Convert amount
# 	amount = groups['amount'].replace(',', '.')
# 	try:
# 		if '.' in amount:
# 			amount = float(amount)
# 		else:
# 			amount = int(amount)
# 	except ValueError as e:
# 		raise ValueError(s) from e

# 	qual = groups['qual'] or ''
# 	if not qual:
# 		return amount

# 	if qual[1:2] == 'i':  # Use [x:y] notation to avoid exceptions
# 		base = 1024
# 	else:
# 		base = 1000
# 		qual = qual[0:1]

# 	raise NotImplementedError()
