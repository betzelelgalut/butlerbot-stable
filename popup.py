#!/usr/bin/python

# python program to replace bash script version of popup
# example code can be found here
# http://stackoverflow.com/questions/1605520/how-to-launch-and-run-extenal-script-in-background
# thanks to charlie from the charlix project for this advice.
import sys, os
sys.path.append(os.getcwd(/bin))
sys.path.append(os.getcwd(/sbin))
sys.path.append(os.getcwd(/usr/bin))
sys.path.append(os.getcwd(/usr/sbin))
sys.path.append(os.getcwd(/usr/local))
sys.path.append(os.getcwd(/usr/local/bin))
sys.path.append(os.getcwd(/opt))
sys.path.append(os.getcwd(/home))
sys.path.append(os.getcwd(/var))
sys.path.append(os.getcwd(/cdrom))
sys.path.append(os.getcwd(/mnt))
sys.path.append(os.getcwd(/media))
###################
# launches app in a new shell
os.system("python test.py")
subprocess.Popen("python test.py", shell=True)

# for the test.py script
####################
#for i in range(0, 1000000):
#    print i