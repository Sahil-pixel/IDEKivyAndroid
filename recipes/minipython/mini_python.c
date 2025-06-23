#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>

void preload_libpython_global() {
    const char *libpython = "libpython3.11.so";
    void *handle = dlopen(libpython, RTLD_NOW | RTLD_GLOBAL);
    if (!handle) {
        fprintf(stderr, "Failed to dlopen %s: %s\n", libpython, dlerror());
    } else {
        fprintf(stderr, "Preloaded %s with RTLD_GLOBAL\n", libpython);
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Usage: mini_python script.py\n");
        return 1;
    }

    //  Ensure libpython symbols are globally available
    preload_libpython_global();

    // Set program name for embedded Python
    wchar_t *program = Py_DecodeLocale(argv[0], NULL);
    if (!program) {
        fprintf(stderr, "Fatal error: cannot decode argv[0]\n");
        return 1;
    }
    Py_SetProgramName(program);

    //Initialize Python runtime
    Py_Initialize();

    // Convert argv to wchar_t**
    wchar_t **argv_w = (wchar_t **)malloc(sizeof(wchar_t *) * argc);
    if (!argv_w) {
        fprintf(stderr, "Fatal error: cannot allocate memory for argv_w\n");
        return 1;
    }

    for (int i = 0; i < argc; ++i) {
        argv_w[i] = Py_DecodeLocale(argv[i], NULL);
        if (!argv_w[i]) {
            fprintf(stderr, "Fatal error: cannot decode argv[%d]\n", i);
            return 1;
        }
    }

    //Set sys.argv inside Python
    PySys_SetArgv(argc, argv_w);

    // Run the script file
    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        fprintf(stderr, "Could not open %s\n", argv[1]);
        return 1;
    }

    int result = PyRun_SimpleFile(fp, argv[1]);
    fclose(fp);

    // Finalize Python
    Py_Finalize();

    // Clean up
    PyMem_RawFree(program);
    for (int i = 0; i < argc; ++i) {
        PyMem_RawFree(argv_w[i]);
    }
    free(argv_w);

    return result;
}
