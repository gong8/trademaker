from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

ext_modules = [
  Extension(
    "calc",
    ["calc/simulate.pyx"],
    extra_compile_args=["/Ox", "/openmp"], 
    extra_link_args=["/openmp"],
  )
]

setup(
  ext_modules = cythonize(
    ext_modules, 
    compiler_directives={"language_level" : "3"}
  ),
  include_dirs = [numpy.get_include()],
  package_data = {
    "calc": ["*.pyx"],
  }
)