from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from job import *


# From https://www.the-analytics.club/python-monitor-file-changes
class FileCreateHandler(FileSystemEventHandler):
    def on_created(self, event):
        fullpath = event.src_path
        suffix = Path(fullpath).suffix
        if (suffix == ".txt"):
            print("Analyzing: " + fullpath)
            generate_keywords(fullpath)
            print ("---------\n")

if __name__ == "__main__":

    event_handler = FileCreateHandler()

    # Create an observer.
    observer = Observer()

    # Attach the observer to the event handler.
    observer.schedule(event_handler, "/Users/vik/Downloads", recursive=True)

    # Start the observer.
    observer.start()

    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()