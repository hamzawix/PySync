from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys
import time
import paramiko
import os


class SSHConnector:
    
    def __init__(self, server, user, pwd):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
        self.connect(server, user, pwd)

    def send_ftp(self, src, dst):
        self.sfpt = self.ssh.open_sftp()
        self.sfpt.put(src, dst)
        self.sfpt.close()
        self.ssh.close()


class Handler(FileSystemEventHandler):

    def process(self, event):
        print("source: ",event.src_path)
        print("type: ",event.event_type)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)
    
    def on_modified(self, event):
        self.process(event)
        


if __name__ == '__main__':

    args = sys.argv[1:]
    observer = Observer()
    observer.schedule(Handler(), path=args[0] if args else '.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
