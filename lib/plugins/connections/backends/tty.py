import random
import sys
import time

import backend
import getpass

# This string needs to be defined for each back end.  It should
# contain the name of the back-end class defined in this module.
backEndClass = "BackEndTTY"

# List the default values for the INI file.  This should be a dictionary
# with keys of the form "<be>.<entry>", where <be> is the name of the
# Backend (e.g. "aim", "msn"), and entry is the name of the configuration
# variable (e.g. "username", "password").  All values should be strings.
#
# Each backend must define an "active" entry, whose possible values
# are "yes" and "no", which indicates whether that backend should
# be activated.
configDefaults = {
    "tty.active":       "yes"
    }

class BackEndTTY(backend.IBackEnd):
    """
    A butt-simple class demonstrating the bare minimum needed to
    implement a new back-end for ButlerBot.
    """    
    def go(self):
	#in the future set the _sessionID to grab the local user login name
	# found that getpass.getuser() will echo the name of the currently logged in 
	# user on the tty. 
        self._sessionID = getpass.getuser()

        import bin.agent_butlerbot
	
        bin.agent_butlerbot.kernel.setPredicate("secure", "yes", self._sessionID)
        while True:
            input = raw_input("{:-D %> @ ")
            response = self.submit(input, self._sessionID)
            #time.sleep(random.random() * 4)
            self.display(response, self._sessionID)
    
    def display(self, output, user):
        print output
