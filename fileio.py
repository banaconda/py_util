import os
import subprocess

def make_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_file(path):
    if os.path.isfile(path):
        os.remove(path)
