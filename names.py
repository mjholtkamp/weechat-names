# Copyright (C) 2013 Michiel Holtkamp <weechat@elfstone.nl>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Show nicks in columns.
#
# Usage: /na
#
# History:
# 2013-07-03, Michiel Holtkamp <weechat@elfstone.nl>:
#     version 1.1: ignore 'unknown' modes, use prefix length, code cleanup
# 2013-06-22, Michiel Holtkamp <weechat@elfstone.nl>:
#     version 1.0: initial release
#
import math
import time
import weechat

from operator import itemgetter

def cmp_nick(a, b):
	c = cmp(b[0], a[0]) # reverse sort the prefix so ops (@) are before non-ops
	if c != 0:
		return c

	return cmp(a[1].lower(), b[1].lower())

def _bold(s):
	return "{}{}{}".format(weechat.color("bold"), s, weechat.color("reset"))

def names_command_cb(data, buffer, args):
	max_linelen = 80
	buffer = weechat.current_buffer()
	server = weechat.buffer_get_string(buffer, "localvar_server")
	channel = weechat.buffer_get_string(buffer, "localvar_channel")
	infolist = weechat.infolist_get("irc_nick", "", "%s,%s" % (server, channel))
	if not infolist:
		return weechat.WEECHAT_RC_OK

	timefmt = weechat.config_string(
				weechat.config_get("weechat.look.buffer_time_format"))
	formatted = "{} ".format(time.strftime(timefmt))
	list_prefix = " " * len(formatted)

	nicks = []
	maxlen = 0
	modes = {'@': 0, '%': 0, '+': 0, ' ': 0}
	while weechat.infolist_next(infolist):
		nick = weechat.infolist_string(infolist, "name")
		prefix = weechat.infolist_string(infolist, "prefix")
		nicks.append((prefix, nick))
		maxlen = max(maxlen, len(nick))
		try:
			modes[prefix] += 1
		except KeyError:
			pass # unknown prefix, it's ok because we don't show it
	weechat.infolist_free(infolist)

	nicks.sort(cmp_nick)
	# +4 = +prefix +[] +space
	nicks_per_line = (max_linelen - len(list_prefix)) // (maxlen + 4)
	rows = int(math.ceil(float(len(nicks)) / nicks_per_line))
	fmt = "{}[{}{}{}{}{: <%d}{}]{} " % maxlen

	prefix = weechat.prefix("network")
	bracket = weechat.color("black")
	title = weechat.color("green")
	bold = weechat.color("bold")
	reset = weechat.color("reset")

	# now that we have all information, print it
	weechat.prnt(buffer, "{}{}[{}Users {}{}{}]{}".format(
			prefix, bracket, title, bold, channel, bracket, reset))

	for row in xrange(rows):
		line = "\t\t%s" % list_prefix
		for col in xrange(nicks_per_line):
			try:
				nick = nicks[col * rows + row]
			except IndexError:
				break
			line += fmt.format(bracket, reset, bold, nick[0], reset,
								nick[1], bracket, reset)
		weechat.prnt(buffer, line)
	
	weechat.prnt(buffer,
		"{}{}: {} nicks ({} ops, {} halfops, {} voices, {} normals)".format(
			prefix, _bold(channel), _bold(len(nicks)), _bold(modes['@']),
			_bold(modes['%']), _bold(modes['+']), _bold(modes[' ']),
		)
	)

	return weechat.WEECHAT_RC_OK

weechat.register("names", "Michiel Holtkamp", "1.1", "GPL3", "Names script", "", "")
weechat.hook_command("na", "Show nicks in columns instead of a list",
	"",
	"",
	"",
	"names_command_cb",
	"")


