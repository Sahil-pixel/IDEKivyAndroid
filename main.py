# Author: SK Sahil (Sahil-Pixel)
# GitHub: https://github.com/Sahil-pixel
#
# Co-authors:
#   Kartavya Shukla (Novfensec) - https://github.com/Novfensec
#   psychowasp                - https://github.com/psychowasp
#
# Created: June 2025
# Purpose: Custom IDE using Kivy for Android with isolated Python interpreter
#          Supports multiprocessing via native mini_python executable

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from jnius import autoclass
import os
import shutil
import math
# Embedded Python script to run

SCRIPT_CODE="""
import sys
import os
print("Hello from embedded script!", flush=True)
print("Python version:", sys.version, flush=True)
print("Script path:", __file__, flush=True)

from multiprocessing import Process
import time
import os

def worker():
    print("In subprocess: PID =", os.getpid(), flush=True)
    for i in range(3):
        print(f"Subprocess count: {i}", flush=True)
        print("Python multiprocessing works on Android Kivy App")
        time.sleep(0.5)

if __name__ == '__main__':
    print("In main process: PID =", os.getpid(), flush=True)
    p = Process(target=worker)
    p.start()
    p.join()
    print("Subprocess finished", flush=True)


"""

SCRIPT_CODE1="""

import sys
import os
print("Hello from embedded script!",flush=True)
print("sys.path =", sys.path, flush=True)
print("LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH", ""), flush=True)
print("PYTHONPATH =", os.environ.get("PYTHONPATH", ""), flush=True)

import importlib.util
print("math module spec:", importlib.util.find_spec("math"), flush=True)import kivy
import math
print(math.cos(10),flush=True)
print("Python version:", sys.version,flush=True)
print("2 + 2 =", 2 + 2,flush=True)
print("Python IDE runs python scripts",flush=True)
import sqlite3
for i in range(5):
    print("Python IDE Using Kivy",flush=True)
"""


import zipfile

#kivy app use zipimport to import stdlib from zip for our case we should extract this for mini_python
def extract_stdlib_if_needed(stdlib_zip_path, target_dir):
    if not os.path.exists(os.path.join(target_dir, 'encodings', '__init__.pyc')):
        try:
            with zipfile.ZipFile(stdlib_zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
                print(f"Extracted stdlib.zip to {target_dir}")
        except Exception as e:
            print(f"Failed to extract stdlib.zip: {e}")



class PythonRunner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.output = TextInput(readonly=True, size_hint_y=1.0, font_size=40)
        self.add_widget(self.output)
        Clock.schedule_once(self.run_script, 1)

    def run_script(self, *args):
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            files_dir = context.getFilesDir().getAbsolutePath()
            lib_dir = context.getApplicationInfo().nativeLibraryDir
            files = os.listdir(lib_dir)
            print("Files in nativeLibraryDir:")
            for f in files:
                print(f)

            stdlib_zip_path = os.path.join(files_dir, 'app/_python_bundle/stdlib.zip')
            stdlib_extract_path = os.path.join(files_dir, 'app/lib/python3.11')
            extract_stdlib_if_needed(stdlib_zip_path, stdlib_extract_path)


            # Paths
            script_path = os.path.join(files_dir, 'script.py')
            #libmini_python.so is Executable not shared object 
            mini_python_src = os.path.join(lib_dir, 'libmini_python.so')
            print("====##====",mini_python_src)
            

            # Save script.py for testing 
            with open(script_path, 'w') as f:
                f.write(SCRIPT_CODE)

           

            # Run with ProcessBuilder
            ArrayList = autoclass('java.util.ArrayList')
            cmd = ArrayList()
            cmd.add(mini_python_src)
            cmd.add(script_path)

            ProcessBuilder = autoclass('java.lang.ProcessBuilder')
            pb = ProcessBuilder(cmd)
            pb.redirectErrorStream(True)
            env = pb.environment()
            

            #PythonActivity = autoclass('org.kivy.android.PythonActivity')
            #context = PythonActivity.mActivity
            #files_dir = context.getFilesDir().getAbsolutePath()
            #os.makedirs(f"{files_dir}/app/lib/python3.11/lib-dynload", exist_ok=True)
            #shutil.copy(
            #f"{files_dir}/app/_python_bundle/modules/math.cpython-311.so",
            #f"{files_dir}/app/lib/python3.11/lib-dynload/"
            #)
            
            env_vars = {
                "PYTHONHOME": f"{files_dir}/app",
                "PYTHONPATH": ":".join([
                    f"{files_dir}/app",
                    f"{files_dir}/app/lib",
                    f"{files_dir}/app/lib/python3.11",
                    f"{files_dir}/app/lib/python3.11/lib-dynload",  # <- must include this
                    f"{files_dir}/app/_python_bundle/site-packages",
                    f"{files_dir}/app/_python_bundle/modules"
                ]),
                "LD_LIBRARY_PATH": ":".join([
                    f"{files_dir}/app/_python_bundle/modules",
                    f"{files_dir}/app/lib",
                    lib_dir,
                    
                ]),
                "TMPDIR": f"{files_dir}"
            }



           
            for key, value in env_vars.items():
                env.put(key, value)


            process = pb.start()

            Scanner = autoclass('java.util.Scanner')
            # Capture stdout
            scanner = Scanner(process.getInputStream()).useDelimiter("\\A")
            output = scanner.next() if scanner.hasNext() else 'No output.'

            # Capture stderr
            error_stream = process.getErrorStream()
            err_scanner = Scanner(error_stream).useDelimiter("\\A")
            error_output = err_scanner.next() if err_scanner.hasNext() else ''

            # Combine both
            self.output.text = output + "\n[stderr]\n" + error_output

        except Exception as e:
            self.output.text = f"[Error] {e}"

class MiniPythonApp(App):
    def build(self):
        return PythonRunner()

if __name__ == '__main__':
    MiniPythonApp().run()
