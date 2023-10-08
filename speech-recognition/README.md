Everything was tested on a Ubuntu 22.04 as well as Ubuntu 20.04.
To use this speech module for pepper you will need both a python2.7 and a python 3.1o installation on your system. 

sudo apt install python2
sudo apt install python3

The python 2 instance is used exclusively to communicate with the robot through pynaoqi. Pynaoqi can be downloaded at this address:
https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz

A tutorial for a naoqi installation can be found here, this is for the non pepper version however.
http://wiki.ros.org/nao/Tutorials/Installation

To Install naoqi for pepper here are the necessary steps:

$ mkdir ~/naoqi
$ cd ~/naoqi
$ wget https://community-static.aldebaran.com/resources/2.5.10/Python%20SDK/pynaoqi-python2.7-2.5.7.1-linux64.tar.gz

tar xzf naoqi-sdk-2.1.4.13-linux64.tar.gz

$ echo 'export PYTHONPATH=/home/USERNAME_HERE/naoqi/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages' >> ~/.bashrc

At this point open a new console to have the correct pythonpath.

$ echo $PYTHONPATH
should now return 
/home/USERNAME/naoqi/pynaoqi-python2.7-2.5.7.1-linux64/lib/python2.7/site-packages:$PYTHONPATH

you can check the installation by using 
$python2
>>> from naoqi import ALProxy

if this causes the importerror
ImportError: libpython2.7.so.1.0: cannot open shared object file: No such file or directory
you can install this using 
$ sudo apt-get install libpython2.7
$ sudo apt-get install libatlas3-base

The last python2 requirements are paramiko and scp
python3 -m pip install paramiko
python3 -m pip install scp


All other dependencies can be installed using pip. By default this should be installed for the main, python3 instance however this can be managed by using 
$ python3 -m pip install MODULE

required modules are in requirements.txt.

whisper needs to be installed using 
$ pip install git+https://github.com/openai/whisper.git 

$ sudo apt update && sudo apt install ffmpeg
