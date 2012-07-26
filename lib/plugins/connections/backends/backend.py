"""
Abstract base class upon which all back-ends are built.
"""

class IBackEnd:
    def __init__(self):
        pass

    def go(self):
        print ("OVERLOAD ME!")
        pass

    def submit(self, input, user):
        """Submits a line of input for ButlerBot to process, from a particular user."""
        # must delay this import until now to prevent circular references
        import bin.agent_butlerbot 
        return bin.agent_butlerbot.submit(input, user)

    def display(self, output, user):
        """Displays output for the specified user."""
        pass
    
