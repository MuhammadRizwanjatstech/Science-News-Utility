#! /usr/bin/env python

import disqus, sys
from datetime import datetime
from BeautifulSoup import BeautifulStoneSoup
 
# globals
TAB = ''
TABSTOP = '    '
DEBUG = 1
idhash = dict()	# lookup table for jskit guid -> disqus comment id

# edit these for your own use
inputfile = sys.argv[1] # xml file name from command line 
user_api_key = 'YOU_API_KEY_HERE' # your disqus account api key
forum_index = 2 # the forum (i.e. site) where you'll be putting comments
				# figure this one out by guess-and-check

def main():
	# bookkeeping
	nthreads = 0;
	ncomments = 0;
	nthcreated = 0;
	ncomcreated = 0;

	# disqus setup
	dsq = disqus.DisqusService()
	dsq.login(user_api_key)
	#dsq.set_debug(1)
	dsqforum = dsq.get_forum_list()[forum_index]
	dprint('Disqus forum prepped: '+dsqforum.name)

	# parse input
	jsksoup = BeautifulStoneSoup(open(inputfile))
	dprint('BeautifulSoup xml parser prepped.')

	# get the jsk threads from input
	dprint('Parsing threads from input file...')
	threads = jsksoup.findAll('channel')

	dprint(str(len(threads))+' threads:')
	nthreads += len(threads)

	dtab()
	for thread in threads:
		thtitle = thread.find('title').contents[0]
		thid = thread.find('jskit:attribute',{'key':'path'})['value']

		dprint('Thread: '+thid)

		comments = thread.findAll('item')
		dprint(str(len(comments))+' comments:')
		ncomments += len(comments)

		jskcomments = list()

		dtab()
		for comment in comments:
			jskcom = dict()
			jskcom['guid'] = comment.find('guid').contents[0]
			jskcom['ip'] = comment.find('jskit:attribute', {'key' : 'IP'})['value']
			jskcom['name'] = comment.find('author')
			if jskcom['name']:
				jskcom['name'] = jskcom['name'].contents[0]
				jskcom['email'] = jskcom['name'].replace(' ','_')+'@jskit.jueseph.com'
			else:
				jskcom['name'] = 'Guest'
				jskcom['email'] = 'guest@jskit.jueseph.com'
			jskcom['url'] = None
			jskcom['msg'] = comment.find('description').contents[0]
			datestring = comment.find('pubdate').contents[0]
			jskcom['created'] = datetime.strptime(datestring,'%a, %d %b %Y %H:%M:%S +0000')
			parent = comment.find('jskit:parent-guid')
			if parent:
				jskcom['parent'] = parent.contents[0]
			else:
				jskcom['parent'] = None

			jskcomments.append(jskcom)

		duntab()

		# put parents before children
		jskcomments = reorder_parentsfirst(jskcomments)
					
		# set up disqus thread
		thurl = 'http://news.sciencemag.org'+thid
		threq = None
		try:
			threq = dsq.get_thread_by_url(dsqforum,thurl)
		except disqus.APIError:
			dprint('Disqus APIError.')

		try:
			if threq:
				dsqthread = threq
			else:
				dsqthread = dsq.thread_by_identifier(dsqforum,title=thid+' comments',identifier=thid)['thread']
				dsq.update_thread(dsqforum,dsqthread,url=thurl)
		except disqus.APIError:
			dprint('Can\'t create thread. Skipping this one.')
			continue

		nthcreated += 1
		# create comments

		dtab()
		for jskcom in jskcomments:
			dprint('JSK Comment. Author: '+jskcom['name']+' | IP: '+jskcom['ip'])
			try:
				dsqcom = dsq.create_post(dsqforum,
							dsqthread,
							jskcom['msg'],
							jskcom['name'].encode('utf-8'),
							jskcom['email'],
							get_dsqparent(jskcom),
							jskcom['created'],
							jskcom['url'],
							jskcom['ip'])
				idhash[jskcom['guid']] = dsqcom.id
				dprint('Disqus comment created: '+dsqcom.id+' (JSK id: '+jskcom['guid']+')') 
				ncomcreated += 1
			except disqus.APIError:
				dprint('APIError in create_post.')
		duntab()

	duntab()

	dprint('Processing complete.')
	dprint('Detected (in import file): '+str(ncomments)+' comments; '+str(nthreads)+' threads.')
	dprint('Created: '+str(ncomcreated)+' comments; '+str(nthcreated)+' threads.')

# helper functions
def dprint(str):
	if DEBUG == 1: 
		try:
			print TAB+str.encode('utf-8')
		except UnicodeEncodeError:
			print 'UnicodeEncodeError in dprint.'

def dtab():
	global TAB, TABSTOP
	TAB += TABSTOP

def duntab():
	global TAB, TABSTOP
	TAB = TAB[0:len(TAB)-len(TABSTOP)]

def get_dsqparent(jskcom):
	global idhash
	if jskcom['parent']:
		if jskcom['parent'] in idhash:
			return idhash[jskcom['parent']]
	return None

def reorder_parentsfirst(jskcomments):
	out = list()
	i = 0
	while len(jskcomments) > 0:
		#dprint('i='+str(i)+', len(jskcomments)='+str(len(jskcomments)))
		com = jskcomments[i]
		p_id = com['parent']
		if p_id: # search for parent and set i to its index
			#dprint('Parent id: '+p_id)
			found = False
			for j, par in enumerate(jskcomments):
				#dprint('j='+str(j))
				#dprint('Match? '+par['guid'])
				if par['guid'] == p_id:
					i = j
					found = True
					break
			if not found:
				out.append(com)
				del jskcomments[i]
				i = 0
		else:	# no parent, ok to remove element and put into new list
			out.append(com)
			del jskcomments[i]
			i = 0
	return out


main()

