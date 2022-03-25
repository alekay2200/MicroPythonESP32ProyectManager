from sys import argv
import subprocess


#p = subprocess.run("ampy.py --port /dev/tty.wchusbserial537D0207651 ls")
p = subprocess.Popen("ampy --port /dev/tty.wchusbserial537D0207651 run main.py", stdout=subprocess.PIPE, shell=True)

print(p.communicate())
