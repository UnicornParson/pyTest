import subprocess
import threading
import shlex
import hashlib
from pathlib import Path
from time import time
import re

class FileFilter:
    templates = {
        "cpp": r'\.(c|cpp|cc|cxx|h|hpp|hh|hxx|in|inl|inc)$'
    }

    @staticmethod
    def has_template(template)-> bool:
        t = template.lower().strip()
        return (t in FileFilter.templates)
    @staticmethod
    def match(template, fname)-> bool:
        t = template.lower().strip()
        if t not in FileFilter.templates:
            raise IndexError("Invalid template type")

        return re.search(FileFilter.templates[t],fname,re.IGNORECASE) is not None

class Utils:
    @staticmethod
    def remove_base_path(absolute_path: str, base_path: str) -> str:
        """
        Removes the base path from an absolute path using pathlib.
        Returns the relative path if the base is valid; otherwise, returns the original path.
        """
        abs_path = Path(absolute_path).absolute()
        base = Path(base_path).absolute()
        
        try:
            relative = abs_path.relative_to(base)
            return str(relative)
        except ValueError:
            # Base is not a prefix of the absolute path
            return str(abs_path)

    @staticmethod
    def run_command_async(command, callback):
        """
        Runs a command asynchronously and calls the callback upon completion.

        :param command: List of command arguments (e.g., ["ls", "-l"]).
        :param callback: Function to be called with arguments (return_code, stdout, stderr).
        """
        def _run():
            s_cmd = Utils.command_list_to_string(command)
            h = Utils.get_md5(s_cmd)
            ts = time()
            print(f"run[{h}] {s_cmd}")
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            te = time()
            print(f"[{h}] - done. took {float(te-ts):0.4f}s")
            callback(process.returncode, stdout.decode(), stderr.decode())
        
        thread = threading.Thread(target=_run)
        thread.start()
        return thread
    
    @staticmethod
    def command_list_to_string(command):
        return ' '.join(shlex.quote(arg) for arg in command)
    
    @staticmethod
    def lines_in(fname):
        # file can be broken. dont use open-for
        try:
            result = subprocess.run(
                ["wc", "-l", fname],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            p = result.stdout.split()
            return int(p[0])
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(f"cannot count '{fname}'. [{e}]'")

    @staticmethod
    def get_md5(text: str) -> str:
        md5_hash = hashlib.md5()
        md5_hash.update(text.encode('utf-8'))
        return md5_hash.hexdigest()