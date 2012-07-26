#!/usr/bin/env python

# Add the current directory to the python search path
import sys, os
#sys.path.append("../lib/plugins/connections")
from AIMLBayes import AIMLBayes
import re
#import aiml
import Kernel
import time
import string
import configFile
from string import upper

class AIMLBot:

#  An AIML chat bot that attempts to use a Bayesian guesser to 
#  reduce the amount of AIML that needs to be written, allowing
#  us to just write very generic AIML and train the filter accordingly.
#  Ideally the bot should ask for help whenever it cannot find a reponse.
# AIMLBot also intends to be highly extensible by allowing for callbacks
#  to be inserted in the AIML using 'handler' predicates. You can extend 
#  this class and supply your own AIML and callbacks which will execute
#  once the bot is fully trained.
# 
#  Duncan Gough 13/03/04
#  
#  - Updated to switch from AIM to IRC, switching TocTalk for Twisted IRC.
#  - Renamed on_IM_IN to on_MSG_IN since we don't handle IMs anymore
#  - Removed all the AIM Buddy code
#  - Also updated to fix a bug with the training mode whereby topics with
#  an underscore were not being learnt. Since we used TRAINING_NICKNAME
#  to teach the bot, learning was effectively disabled. AIMLBot now creates
#  a training file with the topic of TRAININGNICKNAME which means that all
#  the other pieces join up.
#        
#  Duncan Gough 11/01/09

	def __init__(self): # name
		self.blist = {}
		self.response = ''
		self.typerate = 0.05
		self._dir = dir(self)
		
		print("Initialize the back-ends.")
		# Fetch the configuration info
		config = lib.aiml.configFile.get()
		# Initialize the AIML interpreter
		self.kernel = aiml.Kernel()
		#extract config options
		try: verbose = config["general.verbose"] == "yes" or config["cla.verboseMode"] == "yes"
		except: verbose = False
		try: botName = config["general.botname"]
		except: botName = "Nameless"
		try: botMaster = config["general.botmaster"]
		except: botMaster = "The Master"
		try: sessionsPersist = config["general.sessionspersist"].lower() in ["yes", "y", "true"]
		except: sessionsPersist = False
		try: sessionsDir = config["general.sessionsdir"]
		except: sessionsDir = "var/sessions"
		self.kernel.verbose(1)
		self.kernel.setPredicate("secure", "yes") # secure the global session
		self.kernel.bootstrap(learnFiles="lib/aiml/data/aiml/startup.xml", commands="bootstrap")
		self.kernel.setPredicate("secure", "no") # and unsecure it.
		self.kernel.setBotPredicate("name",name)

		# Initialize bot predicates
		for k,v in config.items():
			if k[:8] != "botinfo.":
				continue
			kernel.setBotPredicate(k[8:], v)
		
		# Initialise the Bayes parser
		self.bayes = AIMLBayes(name)

		# Load persistent session data, if necessary
		if sessionsPersist:
			try:
				for session in os.listdir(sessionsDir):
					# Session files are named "user@protocol.ses", where
					# user@protocol is also the internal name of the session.
					root, ext = os.path.splitext(session)
					if ext != ".ses":
						# This isn't a session file.
						continue
					# Load the contents of the session file (a single dictionary
					# containing all the predicates for this session).
					if verbose: print ("Loading session:"), root
					f = file("%s/%s" %(sessionsDir, session), "rb")
					d = marshal.load(f)
					f.close()
					# update the predicate values in the Kernel.
					for k,v in d.items():
						kernel.setPredicate(k,v,root)
			except OSError:
				print ("WARNING: Error loading session data from"), sessionsDir
	
		# Handle local mode: only start the tty backend
		if config['cla.localMode'].lower() in ["yes", "y", "true"]:
			try: _addBackEnd("tty", "BackEndTTY")
			except:
				print ("ERROR initializing backend class backends.tty.BackEndTTY")
				traceback.print_tb(sys.exc_info()[2])
		else:
			# Initialize the back-ends.  Pythonic black magic ensues...
			# First we iterate over all backend modules.
			for be in backends.__all__:
				# If this backend isn't activated in the configuration file,
				# ignore it.
				try: isActive = (config["%s.active" % be].lower() in ["yes", "y", "true"])
				except KeyError:
					print ("WARNING: no 'active' entry found for module %s in configuration file.") % be
					isActive = False
				if not isActive:
					if config['cla.verboseMode'] == 'yes':
						print ("Skipping inactive frontend: %s") % be
					continue

				# Attempt to extract the name of the back-end class defined in this module.
				# If no such class is defined, or if the class is not a subclass of IackEnd,
				# skip this module.
				try:
					cls = eval("backends.%s.backEndClass" % be)
					if not issubclass(eval("backends.%s.%s" % (be, cls)), backends.backend.IBackEnd):
						continue
				except AttributeError:
					# no valid back-end class defined in this file.
					print ("WARNING: could not find valid back-end class in module %s") % be
					continue

				# Create an instance of this class in the _backends dictionary
				try: _addBackEnd(be, cls)
				except:
					# raise # uncomment for details on error
					print ("ERROR initializing backend class backends.%s.%s") % (be,cls)
					traceback.print_tb(sys.exc_info()[2])
					continue
				

	def do_RESPONSE(self,sn,reply):

	#Sends the AIML response back to the other user.
	#Typing timeout code written by Michael Wakerly
		for sentence in reply.split("\n"):
			# Pretend we are typing with an artificial timeout
			slept = 0

	
			
		for char in sentence:
			time.sleep(self.typerate)
			slept += self.typerate
			if slept >= 5.0:
				break

		self.response = sentence

	def fetch_aiml_response(self,line,sn):
		#Returns the response from the AIML parser

		try:
			return self.kernel.respond(line,sn)
		except:
			return None

	def guess(self,line):

	#Guess the topic of conversation using a Bayesian filter

		try:
			topic = self.bayes.guess(line)[0][0]
			print "[Guess] %s" % topic
			return topic
		except:
			return None


	def on_BAYES(self,sn,line,topic=""):
		#Guess the topic and then try to find a reponse.
		#If that fails, ask for help.
		if topic:
			try:
				print ("[Topic] %s") % topic
				self.kernel.setPredicate("topic",topic,sn)
				reply = self.fetch_aiml_response(line,sn)
				if reply:
					self.do_RESPONSE(sn,reply)
				else:
					self.on_UNKNOWN(sn,line)
			except:       
				self.on_UNKNOWN(sn,line)
		else:
			try:
				topic = self.bayes.guess(line)[0][0]
				print ("[Topic] %s") % topic
				self.kernel.setPredicate("topic",topic,sn)
				reply = self.fetch_aiml_response(line,sn)
				if reply:
					self.do_RESPONSE(sn,reply)
				else:
					self.on_UNKNOWN(sn,line)
			except:
				self.on_UNKNOWN(sn,line)


	def on_FORGET(self,sn,line):
		#Purposefully forget information stored in the Bayesian filter
		tmp = self.kernel.getPredicate("meaning",sn)
		meaning,topic = tmp.split("means")
		self.bayes.untrain(topic.strip(),meaning.strip())

		# We don't want this topic to persist
		self.kernel.setPredicate("topic","",sn)

	def on_MSG_IN(self,sn,data):
		#Main method called in reponse to an incoming message
		line,sn = self.parse_msg(data,sn)

		guess = self.guess(line)
		topic = self.kernel.getPredicate("topic",sn)
		handler = self.kernel.getPredicate("handler",sn)

		# Order of relevance:
		# 1. Handler set by AIML (mainly used for training)
		# 2. Bayesian guess (whether the topic agrees or not)
		# 3. Persistent topic
		# 4. Ask for help

		if ("on_%s" % handler ) in self._dir:
			# Handle further implementations (borrowed from PyTOC in the old GrokItBot code)
			print ("[Handler] %s") % handler
			exec ( "self.on_%s(sn,line)" % handler )
		elif guess == topic:
			# Persistant topic, which Bayes agrees with
			self.on_TOPIC(sn,line)
		elif guess:
			# Lets try a guess
			self.on_BAYES(sn,line,guess)

		# We can support persistant topics here but that requires much more 
		# training of the bot in the long run, as the topic of conversation 
		# will only change once the bot is able to guess at a change of topic
		# from keywords in your input. Since this can take some time and doesn't
		# show off the Bayes guessing ability so well, I've disabled that.
		# If you want to try this out, just uncomment the following else statement.
		# You'll find the bot will stay on topic and that you'll need to make use of
		# the 'learn x' statement to train the bot accordingly.
		#
		elif topic:
			# Stay on topic
			self.on_TOPIC(sn,line)

		else:
			# Last resort.. another guess
			self.on_BAYES(sn,line)

			# Finally, check for and carry out any callbacks set in
			# the AIML (barring training, which requires one more input)
			handler = self.kernel.getPredicate("handler",sn)

		if ("on_%s" % handler ) in self._dir:
			# Handle further implementations (just as PyTOC does)
			if handler != "TRAINING":
				print "[Callback] %s" % handler
				exec ( "self.on_%s(sn,line)" % handler )
				self.kernel.setPredicate("handler","",sn)

		return self.response


	def on_NEVERMIND(self,sn,line):

		#Just a get out clause that resets topics and handlers

		self.kernel.setPredicate("topic","",sn)
		self.kernel.setPredicate("handler","",sn)
		self.do_RESPONSE(sn,"OK, forget it")

	def on_RELOAD(self,sn,line):
		#Causes the bot to reload its' AIML files

		reply = self.fetch_aiml_response(line,sn)
		self.do_RESPONSE(sn,reply)

	def on_SAVEBRAIN(self,sn,topic):

		#Save the bayes file to disk

		self.bayes.save()
		self.do_RESPONSE(sn,"OK, saved it")

	def on_TOPIC(self,sn,line):

		#A topic is already set, try and find a reponse for it.
		#If that fails, let the bayes filter try its' luck

		reply = self.fetch_aiml_response(line,sn)

		if reply:
			self.do_RESPONSE(sn,reply)
		else:
			self.on_BAYES(sn,line)

	def on_TRAINING(self,sn,line):

		#Use the AIML response as a keyword, the users response as
		#an explanation and train the bayesian filter accordingly

		self.kernel.setPredicate("topic","training" + sn,sn)
		topic = self.fetch_aiml_response(line,sn)
		meaning = self.kernel.getPredicate("meaning",sn)

		if topic == "NEVERMIND":
			self.on_NEVERMIND(sn,line)
		else:
			try:
				self.bayes.train(topic,meaning)
				self.do_RESPONSE(sn,"OK, I grok that")
			except:
				self.do_RESPONSE(sn,"Sorry, that didn't work")

		# Reset the various training flags
		self.kernel.setPredicate("topic","",sn)
		self.kernel.setPredicate("handler","",sn)

	def on_UNKNOWN(self,sn,line):

		#Ask the user for help. The AIML parser will generate a dynamic AIML
		#file which it can learn, in anticipation of a meaningful reply

		self.kernel.setPredicate("topic","unknown",sn)
		reply = self.fetch_aiml_response(line,sn)
		self.do_RESPONSE(sn,reply)
		self.kernel.setPredicate("topic","",sn)


	def parse_msg(self,msg,sn):
		
		#Munge the input and hack any URLs so that they aren't split into 
		#multiple sentences by the AIML parser

		self.kernel.setPredicate("player1",sn,sn)

		line = self.strip_tags(msg)
		line = line.strip()

		m = re.match('^(.*?)(http://)?((?:[a-z0-9-]+\.)?[a-z0-9-]+\.[a-z0-9]+(?:\.[a-z0-9\.]*)?.*$)',line,re.IGNORECASE)
		try:
			url = m.group(3).replace(".","::").replace("?","++")
			line = m.group(1) + url
		except:
			pass

		return line,sn

	def strip_tags(self,value):
		"Return the given HTML with all tags stripped. From http://xrl.us/beb7n7"
		return re.sub(r'<[^>]*?>', '', value)
