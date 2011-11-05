import sys
import urllib.request
import re

if len(sys.argv) != 2:
	print("Usage: %s <wiki-entry>"%(sys.argv[0]))
	sys.exit()

def found(string, num):
	print('#############################')
	print('Hey, we found %s after %u hops...'%(string, num))
	print('#############################')
	sys.exit()

tries = 1
triedSnip = []
def validateUrl(urlSnip):
	global tries, triedSnip
	print('			 Try %u: "%s"...'%(tries, urlSnip), end="")
	for arg in ['wiktionary', 'wikimedia', '.ogg', 'simple.wikipedia', '/File:', '/Wikipedia:']: # Bad keywords
		if arg in urlSnip:
			print("	[bad keyword (%s)]"%(arg), end="\n")
			tries += 1
			return True
	for entry in triedSnip:
		if entry == urlSnip:
			print("	[repetition detected]", end="\n")
			tries += 1
			return True
	if '/wiki' in urlSnip:
		triedSnip.append(urlSnip)
		print("", end="\n")
		return False
	tries += 1
	print("	[no /wiki found]", end="\n")
	return True

def deleteHTMLTags(code, tags):
	for tag in tags:
		pat = '<%s.*?/%s>'%(tag, tag)
		code = re.sub(pat, '', code)
	return code

def doStuff(url):
	global hops, tries, hrefs, hrefsInB
	hops += 1

	c = urllib.request.Request(url)
	c.add_header("User-Agent", "Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.7.3) Gecko/20040924 Epiphany/1.4.4 (Ubuntu)")
	try:
		code = urllib.request.urlopen(c).read()
	except urllib.error.HTTPError:
		print('>>> No valid url given, aborting...')
		sys.exit()
	code = str(code, 'utf-8')
 
	code = deleteHTMLTags(code, ['div', 'span', 'i', 'table'])
	#print code
	inP = re.compile(r'<p>(.+?)</p>').findall(code) # Get relevant text-snippet
	for p in inP:
		#print p
		hrefsInB = re.compile(r'\(.*?<a href="(.*?)".*?\)').findall(p) # Get hrefs surrounded by brackets
		hrefs = re.compile(r'<a href="(.*?)"').findall(p) # Get link value
		#print hrefs
		#print hrefsInB
		# Delete Links in brackets out of normal links-list
		for link in hrefs:
			for linkB in hrefsInB:
				if link == linkB:
					hrefs.remove(link)
		if len(hrefs) != 0:
			break
	try:
		checker(hrefs)
	except IndexError:
		print(">>> No normal links found, now trying with the ones in brackets...")
		try:
			checker(hrefsInB)
		except IndexError:
			print(">>> No links in brackets found...")
			if 'may refer to:' in code:
				print(">>> We are on a selection page...")
				liH = []
				inLi = re.compile(r'<li>(.+?)</li>').findall(code)
				for li in inLi:
					checker(re.compile(r'<a href="(.*?)"').findall(li))
			sys.exit()

def checker(links):
	c = 0
	while validateUrl(links[c]):
		c += 1
		if c == len(links):
			print('>>> No validated url found, aborting...')
			sys.exit()
	tries = 1
	print('[%u] %s'%(hops, links[c]))
	if '/wiki/Philosophy' in links[c]:
		found('Philosophy', hops)
	doStuff('http://en.wikipedia.org%s'%(links[c]))

hops = 0

if "http://en.wikipedia.org/wiki/" in sys.argv[1]:
	url = sys.argv[1]
else:
	url = "http://en.wikipedia.org/wiki/%s" % (sys.argv[1])

print('[%u] %s'%(hops, url))

doStuff(url)
