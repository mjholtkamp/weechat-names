import math
import weechat

from operator import itemgetter

def cmp_nick(a, b):
	c = cmp(b[0], a[0]) # reverse sort the prefix so ops (@) are before non-ops
	if c != 0:
		return c

	return cmp(a[1].lower(), b[1].lower())

def names_command_cb(data, buffer, args):
	max_linelen = 72
	buffer = weechat.current_buffer()
	server = weechat.buffer_get_string(buffer, "localvar_server")
	channel = weechat.buffer_get_string(buffer, "localvar_channel")
	infolist = weechat.infolist_get("irc_nick", "", "%s,%s" % (server, channel))
	prefixmaxlen = weechat.buffer_get_integer(buffer, "prefix_max_length")
	max_linelen = max_linelen - (prefixmaxlen + 4)

	if infolist:
		nicks = []
		maxlen = 0
		while weechat.infolist_next(infolist):
			nick = weechat.infolist_string(infolist, "name")
			prefix = weechat.infolist_string(infolist, "prefix")
			nicks.append((prefix, nick))
			maxlen = max(maxlen, len(nick))
		weechat.infolist_free(infolist)

		nicks.sort(cmp_nick)
		nicks_per_line = max_linelen // (maxlen + 4) # +prefix +[] +space
		rows = int(math.ceil(float(len(nicks)) / nicks_per_line))

		bracket = weechat.color("black")
		title = weechat.color("green")
		bold = weechat.color("bold")
		reset = weechat.color("reset")

		fmt = "{}[{}{}{}{}{: <%d}{}]{} " % maxlen

		# now that we have all information, print it
		weechat.prnt(buffer, "{}[{}Users {}{}{}]{}".format(bracket, title, bold, channel, bracket, reset))
		for row in xrange(rows):
			line = ""
			for col in xrange(nicks_per_line):
				try:
					nick = nicks[col * rows + row]
				except IndexError:
					break
				line += fmt.format(bracket, reset, bold, nick[0], reset, nick[1], bracket, reset)
			weechat.prnt(buffer, line)

	return weechat.WEECHAT_RC_OK

weechat.register("names", "sabre2th", "1.0", "GPL3", "Names script", "", "")
weechat.prnt("", "Hello, from python script!")
weechat.hook_command("na", "Names like irssi",
	"None",
	"None",
	"",
	"names_command_cb",
	"")


