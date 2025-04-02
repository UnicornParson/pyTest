import subprocess
import threading
import shlex
import hashlib
from time import time

class Utils:
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
            print(f"[{h}] - done. took {float(te-ts):0.4f}")
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