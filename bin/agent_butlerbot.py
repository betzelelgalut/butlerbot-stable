#!/usr/bin/env python

# Add the current directory to the python search path
import marshal
import sys, os, traceback, threading, random, string, time
from lib.aiml import AIMLBot
from lib.plugins.connections import backends
from lib.plugins.connections.backends import *
import re
import lib.aiml as aiml
from lib.aiml import configFile

sys.path.append(os.getcwd())

class ActiveBackEnd:
	def __init__(self, inst, thread):
		self._inst = inst
		self._thread = thread

_backends = {}
kernel = None

def _addBackEnd(name, cls):
	global _backends
	
	# verbose output
	config = configFile.get()
	if config['cla.verboseMode'] in ["yes", "y", "true"]:
		print( "Creating %s back-end using class %s") % (name, cls)
	
	# Instantiate the backend object
	beInst = eval("%s.%s()" % (name, cls))
	# Create a thread to run this backend
	beThread = threading.Thread(name=name, target=beInst.go())
	beThread.setDaemon(True)
	beThread.start()
	_backends[name] = ActiveBackEnd(beInst, beThread)
	beInst.go

def usage():
	"""Prints a usage message."""
	print __doc__

def init():
	global kernel
	print("Initialize the back-ends.")
	# Fetch the configuration info
	config = configFile.get()

	# Initialize the AIML interpreter
	print ("Initializing AIML interpreter (please be patient)...")
	kernel = aiml.Kernel()
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
	
	# set up the kernel
	
	# load brain file function
	if os.path.isfile("var/brain/standard.brn"):
		print ("Loading Brain File:")
		kernel.bootstrap(brainFile = "var/brain/standard.brn")
		print ("Brain file finished loading!")
	else: # create new brain and save it!
		print ("Creating new Brain file...:")
		print ("Setting verbose modes...")
		kernel.verbose(verbose)
		print ("Securing global session...")
		kernel.setPredicate("secure", "yes") # secure the global session
		print ("Loading AIML files in to Brain...")
		kernel.bootstrap(learnFiles="lib/aiml/data/aiml/startup.xml", commands="bootstrap")
		print ("Unsecuring global session...")
		kernel.setPredicate("secure", "no") # and unsecure it.
		print ("Saving new brain file...")
		kernel.saveBrain("var/brain/standard.brn")
		print ("New Brain file saved!")

	# Initialize bot predicates
	for k,v in config.items():
		if k[:8] != "botinfo.":
			continue
		kernel.setBotPredicate(k[8:], v)

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
				if verbose: print "Loading session:", root
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
		try: 
			_addBackEnd("tty", "BackEndTTY")
		except:
			print ("ERROR initializing backend class backends.tty.BackEndTTY")
			traceback.print_tb(sys.exc_info()[2])
	else:
		# Initialize the back-ends.  Pythonic black magic ensues...
		# First we iterate over all backend modules.
		for be in backends.__all__:
			print ("Initializing: %s") % (be)
			# If this backend isn't activated in the configuration file,
			# ignore it.
			try: isActive = (config["%s.active" % be].lower() in ["yes", "y", "true"])
			except KeyError:
				print ("WARNING: no 'active' entry found for module %s in configuration file.") % be
				isActive = False
			if not isActive:
				if config['cla.verboseMode'] == 'yes':
					print ("Skipping inactive backend: %s") % be
				continue

			# Attempt to extract the name of the back-end class defined in this module.
			# If no such class is defined, or if the class is not a subclass of IBackEnd,
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
def submit(input, session):
	"""Submits a statement to the back-end. Returns the response to the statement."""
	response = kernel.respond(input, session)

	config = configFile.get()	
	# if logging is enabled, write the input and response to the log.
	try:
		if config["general.logging"].lower() in ["yes", "y", "true"]:
			logdir = config["general.logdir"]
			if not os.path.isdir(logdir): os.mkdir(logdir)
			logfile = file("%s/%s.log" % (logdir, session), "a")
			logfile.write(time.strftime("[%m/%d/%Y %H:%M:%S]\n"))
			logfile.write("%s: %s\n" % (session, input))
			logfile.write("%s: %s\n" % (kernel.getBotPredicate("name"), response))
			logfile.close()			
	except KeyError:
		pass

	# If persistent sessions are enabled, store the session data.
	try:
		if config["general.sessionspersist"].lower() in ["yes", "y", "true"]:
			sessionsdir = config["general.sessionsdir"]
			if not os.path.isdir(sessionsdir): os.mkdir(sessionsdir)
			sessionfile = file("%s/%s.ses" % (sessionsdir, session), "wb")
			marshal.dump(kernel.getSessionData(session), sessionfile)
			sessionfile.close()
	except KeyError:
		pass
	return response
