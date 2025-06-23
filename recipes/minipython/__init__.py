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


from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory, ensure_dir
from os.path import join, dirname
import os
import shlex
import subprocess
from shutil import copyfile, copytree
import shutil

class MiniPythonRecipe(Recipe):
    name = 'minipython'
    version = '1.0'
    src_filename = 'mini_python.c'
    depends = ['python3']
    built_libraries = {
        'mini_python': 'mini_python'  # ELF binary we embed in APK
    }

    def get_recipe_env(self, arch):
        env = super().get_recipe_env(arch)

        python_recipe = self.get_recipe('python3', self.ctx)
        python_include = python_recipe.include_root(arch.arch)
        python_lib = python_recipe.link_root(arch.arch)

        # DYNAMIC linking instead of static
        env['CPPFLAGS'] = f'-I{python_include}'
        env['LDFLAGS'] = f'-L{python_lib} -lpython3.11 -llog -landroid -ldl -lm'

        return env

    def get_source(self, arch):
        build_dir = self.get_build_dir(arch.arch)
        ensure_dir(build_dir)

        src = join(dirname(__file__), self.src_filename)
        dst = join(build_dir, self.src_filename)

        if not os.path.exists(dst):
            print(f"[minipython] Copying source from {src} to {dst}")
            copyfile(src, dst)

    def build_arch(self, arch):
        self.get_source(arch)
        build_dir = self.get_build_dir(arch.arch)
        env = self.get_recipe_env(arch)

        with current_directory(build_dir):
            cc = env.get('CC', 'clang')
            cfile = join(build_dir, self.src_filename)
            binfile = join(build_dir, 'mini_python')

            cmd = (
                f"{cc} -o {binfile} {cfile} "
                f"{env['CPPFLAGS']} {env['LDFLAGS']}"
            )

            print(f"[minipython] Compiling with: {cmd}")
            subprocess.check_call(shlex.split(cmd))

            # Copy binary to be included in APK as a shared object
            libs_dir = self.ctx.get_libs_dir(arch.arch)
            ensure_dir(libs_dir)
            final_bin = join(libs_dir, 'libmini_python.so')  # .so ensures inclusion
            copyfile(binfile, final_bin)
            os.chmod(final_bin, 0o755)

           

# Register the recipe
recipe = MiniPythonRecipe()
