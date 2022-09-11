# Watch .conf files
import os
from pathlib import Path
from django.utils.autoreload import autoreload_started


def watch_extra_files(sender, *args, **kwargs):
    watch = sender.extra_files.add
    # List of file paths to watch
    watch_list = [
        'videoclips/tasks.py',
    ]
    for file in watch_list:
        if os.path.exists(file):  # personal use case
            watch(Path(file))


autoreload_started.connect(watch_extra_files)
