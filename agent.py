#!/usr/bin/python3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import paramiko
import os


class SSHConnector:
    
    def __init__(self, server, port, user, pwd):
        self.server = server
        self.port = port
        self.user = user
        self.pwd = pwd

        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.ssh.connect(self.server, self.port, self.user, self.pwd)

    def send_ftp(self, src, dst):
        self.sfpt = self.ssh.open_sftp()
        self.sfpt.put(src, dst)
        self.sfpt.close()
        self.ssh.close()
    
    def send_scp(self, src, dst):
        os.system("sshpass -p {} scp -P {} -r {} {}@{}:{}".format(self.pwd,
        self.port, src, self.user, self.server, dst))

    def command(self, cmd):
        self.ssh.exec_command(cmd)


class Handler(FileSystemEventHandler): 

    def __init__(self, server, port, user, pwd, path):
        
        self.connector = SSHConnector(server, port, user, pwd)
        print("**********************************************************")
        print("----------Connected to {} on port {} as user {}-----------".format(server, port, user))
        print("\n\r")
        self.current_path = path
        if user == "root":
            self.dst = "/root/sync"
        else:
            self.dst = "/home/{}/sync".format(user)


    def process(self, event):
        
        if event.event_type == "created":
            rel_path = os.path.relpath(event.src_path, self.current_path)

            if os.path.isdir(event.src_path):
                self.connector.command(cmd="cd {} && mkdir -p {}".format(self.dst, rel_path))
                print("Created directory: ", rel_path)
            
            elif os.path.isfile(event.src_path):
                if os.path.dirname(event.src_path) == self.current_path:
                    self.connector.command("cd {} && touch {}".format(self.dst, rel_path))
                    print("Created file: ", rel_path)
                else:
                    self.connector.command(cmd="cd {} && mkdir -p {} && touch {}".format(self.dst, 
                    os.path.dirname(rel_path),
                    rel_path))

                    print("Created: ", rel_path)
            else:
                pass
        
        elif event.event_type == "modified":
            rel_path = os.path.relpath(event.src_path, self.current_path)

            if event.src_path == self.current_path:
                pass
            elif os.path.isfile(event.src_path):
                self.connector.send_scp(src=event.src_path, dst=os.path.join(self.dst,
                os.path.dirname(rel_path)))
                print("Modified file: ", event.src_path)
            else:
                pass
        
        elif event.event_type == "deleted":
            rel_path = os.path.relpath(event.src_path, self.current_path)
            
            self.connector.command(cmd="cd {} && rm -r {}".format(self.dst, rel_path))
            print("Deleted: ", rel_path)
        
        else:
            pass

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)
    
    def on_modified(self, event):
        self.process(event)
        


if __name__ == '__main__':

    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(Handler(server=args[0], port=args[1], user=args[2], pwd=args[3], path=args[4]),
    path=args[4] if args else '.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
