#/usr/bin/python
#
"""Try to open a filtered search stream
   And grab the #qanda tagged tweets
   Then spit out the timestamp of the tweet.  
   Which can then be used as an input to another script.  BECAUSE MODADS.

Homepage and documentation: http://dev.moorescloud.com/

Copyright (c) 2012, Mark Pesce.
License: MIT (see LICENSE for details)"""

__author__ = 'Mark Pesce'
__version__ = '1.01.dev'
__license__ = 'MIT'

import sys, os, json, time, stat, threading, string, logging, random
from twitter.oauth_dance import oauth_dance
import twitter

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import holidaysecretapi

finished =  False

# File name for the oauth info
#
# This will work for *NIX systems, not sure for Windows.
#
fn = os.path.join(os.path.expanduser('~'),'.twintrest-oauth')

consumer_secret=con_secret = "tI2hvrIJTEdbFyhGpjfWd9tYjIrwbAZCcIEFd8xNsKk"
consumer_key=con_key = "NPtMDL7fgzC0GC86yjgkg"

# Do we have the correct OAuth credentials?
# If credentials exist, test them.  
# If they fail, delete them.
# If they do not exist or fail, create them.
#
def check_twitter_auth():
	authorized = False
	if os.path.isfile(fn):  # Does the token file exist?
		tokens = twitter.oauth.read_token_file(fn)
		#print 'OAuth tokens exist, will try to authorize with them...'
		twapi = twitter.Twitter(auth = twitter.OAuth(token=tokens[0],
					token_secret=tokens[1],
					consumer_secret=con_secret, 
					consumer_key=con_key))
		try:
			result = twapi.account.verify_credentials()
			twitter_id = result['id']
			twitter_handle = result['screen_name']
			authorized = twapi
		except twitter.TwitterError as e:
			print "Call failed, we don't seem to be authorized with existing credentials.  Deleting..."
			print e
			os.remove(fn)

	if authorized == False:                   # If not authorized, do the OAuth dance
		print 'Authorizing the app...'
		tokens = oauth_dance(app_name='CrypTweet', consumer_key=con_key, consumer_secret=con_secret, token_filename=fn)
		os.chmod(fn, stat.S_IRUSR | stat.S_IWUSR)		# Read/write, user-only
		#
		# Get an open API object for Twitter
		#
		twapi = twitter.Twitter(auth = twitter.OAuth(token=tokens[0],
						token_secret=tokens[1],
						consumer_secret=con_secret, 
						consumer_key=con_key))
		try:	# Is this going to work?
			result = twapi.account.verify_credentials()
			twitter_id = result['id']
			twitter_handle = result['screen_name']
			printme('Good, we seem to be authorized for username %s with id %d' % (twitter_handle, int(twitter_id)))
			authorized = twapi
		except twitter.TwitterError as e:		# Something bad happening, abort, abort!
			print "Call failed, we don't seem to be authorized with new credentials.  Deleting..."
			print e
			os.remove(fn)
			
	return authorized

class StdOutListener(StreamListener):
	""" A listener handles tweets are the received from the stream. 
	This is a basic listener that just prints received tweets to stdout.

	"""
	def on_data(self, data):
		global hashterm, twinkler1		# Gotta have a handle to the twinkler thread object thingy

		if finished:
			sys.exit(0)

		djt = json.loads(data)
		try:
			msg = djt['text']
			#printme(msg)
			msglow = string.lower(msg)			# Convert to lowercase for matching
			if string.find(msglow, hashterm) == -1:
				#logging.error("No match in string, curious.")
				pass
			else:
				#printme(msg)
				twinkler1.insert_match(msg)		# Add a match to the animation

		except KeyError:
			printme("KeyError, skipping...")
			pass

		return True

	def on_error(self, status):
		print status

class Listener(threading.Thread):
	"""If you want to run the Twitter listener on its own thread, use this"""

	def start(self, term='NONE'):
		self.searchterm = term
		"Search term: %s" % self.searchterm
		super(Listener, self).start()

	def run(self):
		print "Listener.run %s" % self.searchterm
		global hashterm, auth, l
		stream = Stream(auth, l)	
		stream.filter(track=[self.searchterm])  # Blocking call.  We do not come back.

		logging.error("Returned from stream, this is not good!")
		sys.exit(-3)

class Twinkler(threading.Thread):
	"""If you want to run the Twitter twinkler on its own thread, use this"""

	def start(self, holiday, r, g, b):	
		self.matches = []
		self.hol = holiday
		self.r = r
		self.g = g
		self.b = b

		# Initialize the twinkles
		self.twinklevals = [ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
		0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
		0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
		0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
		0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]

		super(Twinkler, self).start()

	def insert_match(self, msg):
		#printme("insert_match")
		th = [0, msg]		# Array containing position and message 
		self.matches.append(th)
		printme("depth %d" % len(self.matches))

	def run(self):
		while True:

			# Do some twinkling. Just a touch.
			j = 0
			while j < len(self.twinklevals):
				e = random.uniform(-0.075, 0.075)		# Generate a random twinkle value
				m = self.twinklevals[j] + e
				if (m < -0.5):
					m = -0.5
				else:
					if (m > 0.5):
						m = 0.5

				rv = self.r * (m + 0.5)		# Adjust for range and multiply
				gv = self.g * (m + 0.5)		# Adjust for range and multiply
				bv = self.b * (m + 0.5)		# Adjust for range and multiply
				self.hol.setglobe(j, int(rv), int(gv), int(bv))
				self.twinklevals[j] = m
				j = j+1

			# Now go through and animate the matches
			for thingy in self.matches:
				pos = thingy[0]
				if pos >= self.hol.NUM_GLOBES:
					self.matches.remove(thingy)
				else:
					(ar, ag, ab) = self.hol.getglobe(pos)		# Get the current globe value
					ar = 0x2f
					ag = 0x2f
					ab = 0x2f		# Make it all whiterer, but not too bright
					self.hol.setglobe(pos, ar, ag, ab)
					thingy[0] = thingy[0] + 1		# And move the position along
			try:
				self.hol.render()
			except:
				printme("Something failed on the send, not to worry...")
			time.sleep(0.05)		# 20hz twinkles


def printme(str):
	"""A print function that can switch quickly to logging"""
	#print(str)
	logging.debug(str)

if __name__ == '__main__':	
	logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
	printme('Logging initialized')
	printme("Running listener module from the command line.")	

	if len(sys.argv) < 3:
		print("Usage python twintrest.py searchterm ip-address-of-holiday")
		sys.exit(-1)

	the_hostname = sys.argv[2]
	hashterm = sys.argv[1]

	# Initialize the tug-of-war
	hol = holidaysecretapi.HolidaySecretAPI(addr=the_hostname)
		
	if (check_twitter_auth() == False):
		sys.exit(-2)
	print "Authorized"
	
	tokens = twitter.oauth.read_token_file(fn)

	l = StdOutListener()
	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(tokens[0], tokens[1])

	# Startup the twinkler process
	twinkler1 = Twinkler()
	twinkler1.start(hol, r=0,g=0,b=63)

	# Make a thread for the stream listener
	print hashterm
	macher1 = Listener()
	macher1.start(term=hashterm)


		