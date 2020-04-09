#!/usr/bin/env python

# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2020 ifm electronic gmbh
#
# THE PROGRAM IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
#

import glob
import os
import sys
import pathlib
import platform
import sysconfig
import setuptools
from setuptools.command.install import install
import subprocess
import shutil
import multiprocessing
from setuptools.command.build_ext import build_ext
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

# remove build results
for p in ["nexxT/binary", "nexxT/include", "nexxT/tests/binary"]:
    if os.path.exists(p):
        shutil.rmtree(p, ignore_errors=True)
    if os.path.exists(p):
        shutil.rmtree(p, ignore_errors=True)
    if os.path.exists(p):
        shutil.rmtree(p)
# create platform specific wheel
try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel
    
    class bdist_wheel(_bdist_wheel):
        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            self.root_is_pure = False
            self.root_is_purelib = False
            #if platform.system() == "Linux":
            #    self.py_limited_api = "abi3"
            
        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            # uncomment for non-python extensions
            if platform.system() == "Linux":
                abi = "abi3"
                plat = "manylinux2014_x86_64"
            else:
                abi = "none"
            python = "cp37.cp38.cp39"
            print("plat=", plat)
            return python, abi, plat
            
except ImportError:
    bdist_wheel = None

class InstallPlatlib(install):
    def finalize_options(self):
        install.finalize_options(self)
        # force platlib
        self.install_lib = self.install_platlib    
    
class BinaryDistribution(setuptools.Distribution):
    """Distribution which always forces a binary package with platform name"""
    def has_ext_modules(*args):
        #print("HAS_EXT_MODULES WAS CALLED!")
        return True
   
    def is_pure(*args):
        #print("IS_PURE WAS CALLED!")
        return False
        
    def get_option_dict(self, k):
        res = super().get_option_dict(k)
        if k == "install":
            res["install_lib"] = "platlib"
        #print("GET_OPTION_DICT CALLED:", k, res)
        return res
    
if platform.system() == "Linux":
    p = "linux_x86_64"
    presuf = [("lib", ".so")]
else:
    p = "msvc_x86_64"
    presuf = [("", ".dll"), ("", ".exp"), ("", ".lib")]
    

cv = sysconfig.get_config_vars()
if platform.system() == "Windows":
    cnexT = cv.get("EXT_PREFIX", "") + "cnexxT" + cv.get("EXT_SUFFIX", "")
elif platform.system() == "Linux":
    cnexT = cv.get("EXT_PREFIX", "") + "cnexxT.abi3.so"

build_files = []
for variant in ["nonopt", "release"]:
    build_files.append('nexxT/binary/' + p + '/' + variant + "/" + cnexT)
    for prefix,suffix in presuf:
        build_files.append('nexxT/binary/' + p + '/' + variant + "/" + prefix + "nexxT" + suffix)
        build_files.append('nexxT/tests/binary/' + p + '/' + variant + "/" + prefix + "test_plugins" + suffix)

# ok, this is hacky but it is a way to easily include build artefacts into the wheels and this is 
# the intention here, drawback is that sdist needs to be generated by a seperate setup.py call
if "bdist_wheel" in sys.argv:
    if "sdist" in sys.argv:
        raise RuntimeError("cannot build sdist and bdist_wheel with one call.")
    build_required = True
else:
    build_required = False
    
# generate MANIFEST.in to add build files and include files
with open("MANIFEST.in", "w") as manifest:
    manifest.write("include nexxT/examples/*/*.json\n")
    manifest.write("include nexxT/examples/*/*.py\n")
    manifest.write("include nexxT/core/*.json\n")
    manifest.write("include nexxT/tests/core/*.json\n")
    manifest.write("include workspace/*.*\n")
    manifest.write("include workspace/SConstruct\n")
    manifest.write("include workspace/sconstools3/qt5/__init__.py\n")
    manifest.write("include LICENSE\n")
    manifest.write("include NOTICE\n")
    if build_required:
        manifest.write("include nexxT/include/*.hpp\n")
        for bf in build_files:
            manifest.write("include " + bf + "\n")
        manifest.write("exclude nexxT/src/*.*\n")
        manifest.write("exclude nexxT/tests/src/*.*\n")
    else:
        manifest.write("include nexxT/src/*.*\n")
        manifest.write("include nexxT/tests/src/*.*\n")

if build_required:
    try:
        import PySide2
    except ImportError:
        raise RuntimeError("PySide2 must be installed for building the extension module.")
    cwd = pathlib.Path().absolute()
    os.chdir("workspace")
    subprocess.run([sys.executable, os.path.dirname(sys.executable) + "/scons", "-j%d" % multiprocessing.cpu_count(), ".."], check=True)
    os.chdir(str(cwd))    
    
setup(name='nexxT',
      install_requires=["PySide2 >=5.14.0, <5.15", "shiboken2 >=5.14.0, <5.15", "jsonschema>=3.2.0"], 
      version=os.environ.get("NEXXT_VERSION", "0.0.0"),
      description='An extensible framework.',
      author='Christoph Wiedemann',
      author_email='62332054+cwiede@users.noreply.github.com',
      url='https://github.com/ifm/nexxT',
      license="Apache-2",
      include_package_data = True,
      packages=['nexxT', 'nexxT.interface', 'nexxT.tests', 'nexxT.services', 'nexxT.services.gui', 'nexxT.tests.interface', 'nexxT.core', 'nexxT.tests.core'],
      cmdclass={
        'bdist_wheel': bdist_wheel,
        'install': InstallPlatlib,
      },
      entry_points = {
        'console_scripts' : ['nexxT-gui=nexxT.core.AppConsole:mainGui',
                             'nexxT-console=nexxT.core.AppConsole:mainConsole',
                            ]
      },
      distclass=BinaryDistribution,
     )
