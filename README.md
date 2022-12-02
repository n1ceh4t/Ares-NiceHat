# Ares-NiceHat

Fork of https://github.com/sweetsoftware/Ares

EDIT: I hadn't realized at first, but this fork uses Python 3.

![Screenshot](Images/ss1.png?raw=true "Define User")
![Screenshot](Images/ss2.png?raw=true "Client List")
![Screenshot](Images/ss3.png?raw=true "Shell")

+ Ported Server and Client to Python 3
+ Added username to login for 'better security'
+ C++ client source included.
  - Currently working on a windows port written in native c++
  - Credit to the http request library goes to: https://github.com/elnormous/HTTPRequest
  - Reworked the UI a tad.
  - Simple obfuscation for the requests between client and server.
  - Added catch-all for IP addresses whose location were unable to be determined.
  
  As far as I can tell:
  If anything, I removed (or have yet to implement) many features of the bot itself.
  
+ Bugs
  - currently the crypts and decrypts functions have broken the username/hostname/os POST request data (server-side I believe. This is on the to-do list.)

I may include files/instructions for scantime obfuscation (for at least the python client) in the future.

I have omitted many added features and the windows build entirely (using python and nuitka, native c++ WIP) because frankly,
it would be irresponsible to release. 

This is a WIP for self-study. 
Use at your own risk. 
Updates will be sparse, if any are made.

Usage:
    To set up the server:
    
        Nicehat@Nicehat:Python/server_encryption_test$ python3 -m pip install -r requirements.txt
        
        Nicehat@Nicehat:Python/server_encryption_test$ python3 ares.py initdb
        
        Nicehat@Nicehat:Python/server_encryption_test$ python3 ares.py runserver -h 0.0.0.0 -p 8080 --threaded
        
        Navigate to http://127.0.0.1:8080 to set up username and password.
        
    Running the server on windows will require some tweaking but is possible as far as the python modules go IIRC. 
        
    You will have to manually define the server/port in the source files for the bot(s.)

It's difficult to recall all the changes I made to the original if I'm being honest. 
Many thanks to https://github.com/sweetsoftware/ for giving me something interesting and fun to hyperfocus on.

