#! /usr/bin/env python
import sys, os
sys.path.append(os.getcwd())
import commands
import urllib


class Tools:
	"""
	Generic tools class for use over IM
	"""
	def __init__(self):
		data = sys.argv[1:]

		method = data[0]

		try:
			self.line = data[1]
		except:
			pass

		self.dispatch = {
			"uptime" : self.uptime,
		}
		
		try:
			self.dispatch[method]()
		except:
			pass	

	
# Unix / linux tools	
	
	
	def uptime(self):
		"""
		Return the output from uptime
		"""
		print commands.getoutput("uptime")
		
		
	


	def ls(self):
		"""
		lists the dir structure
		"""
		print commands.getoutput("ls -lc")

		
		
	def htop(self):
		"""
		Shows running processes
		"""
		print commands.getoutput("htop")	
	
	
	
	def ps(self):
		"""
		shows processes running
		"""
		print commands.getoutput("ps -aux")	
	
	
	
	def sudo(self):
		"""
		running program as root
		"""
		print commands.getoutput("sudo bash")



	def uname(self):
		"""
		shows OS and server
		"""
		print commands.getoutput("uname -a")

	def nano(self):
		"""
		simple cli txt editor
		"""
		print commands.getoutput("nano")


	def mc(self):
		"""
		cli file manager simular to dos 5
		"""
		print commands.getoutput("mc")
		
		
		

	def ngrep(self):
		"""
		shows output of network traffic in hex dumps
		"""
		print commands.getoutput("ngrep")
		
		
		
		
		
	def dmidecode(self):
		"""
		shows all info that is in the proc file system
		"""
		print commands.getoutput("dmidecode | less")



	def less(self):
		"""
		alows to sroll output up and down
		"""
		print commands.getoutput("less")
		
		
		
		
		
	def more(self):
		"""
		allows to show output scrolling down
		"""
		print commands.getoutput("more")

		
		
		
		
		
	def untar(self):
		"""
		untars a file
		"""
		print commands.getoutput("tar xfvz")		
		
		
		
		
		
	def zip(self):
		"""
		uses 7zip to decompress a *.7z file
		"""
		print commands.getoutput("7z a -t7z -m0=lzma -mx=9 -mfb=64 -md=32m -v650m -ms=on ")	



	def iptraf(self):
		"""
		shows network traffic going through a system.
		"""
		print commands.getoutput("sudo iptraf")	



		
		
		
	

if __name__ == "__main__":
	Tools()