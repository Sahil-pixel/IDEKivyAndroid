# IDEKivyAndroid (Kivy-based Android Python Runner)

**Author:** SK Sahil ([@Sahil-Pixel](https://github.com/Sahil-pixel)  
**Co-authors:**  
- Kartavya Shukla ([@Novfensec](https://github.com/Novfensec))  
- psychowasp ([@psychowasp](https://github.com/psychowasp))  

---

## 📌 Overview

**IDEKivyAndroid** is a custom Python IDE for Android built with **Kivy** that executes Python scripts using an **isolated native Python interpreter**. It features:

- A graphical interface for  viewing output
- Embedded Python interpreter (`mini_python`) compiled as a native executable
- Support for Python’s `multiprocessing` module on Android
- Full integration of Python's standard library and native modules (e.g. `math`, `sqlite3`)

This makes it ideal for Python education, quick script testing, and multiprocessing demonstrations directly on Android devices 

---

## 🚀 Features

- ✅ Kivy GUI with text-based output viewer
- ✅ Embedded and user-defined script execution
- ✅ Native `mini_python` ELF binary linked with `libpython3.11.so`
- ✅ Support for `multiprocessing` using `Process`
- ✅ Dynamic extraction of `stdlib.zip` from assets
- ✅ Environment setup using Java's `ProcessBuilder`
- ✅ Custom `Recipe` for `python-for-android`

---

## 📱 How It Works

1. **App UI** is built with Kivy (`main.py`) and embeds a script (`SCRIPT_CODE`).
2. **Python script** is written to a file (`script.py`) at runtime.
3. **mini_python**, a native ELF executable, is invoked via `ProcessBuilder`.
4. The Python environment (`PYTHONPATH`, `LD_LIBRARY_PATH`, etc.) is configured dynamically.
5. Standard library is unzipped if needed (`stdlib.zip`) to support modules.
6. Script output and errors are displayed in the Kivy interface.

---

## 🔧 Build Setup

### Prerequisites

- Python 3.11
- `python-for-android`
- `buildozer`
- Android NDK (via `buildozer`)

# Setup On Buildozer side 
- p4a.local_recipes = ./recipes
- requirements = python3,kivy,minipython
# To Build  
- buildozer android debug

