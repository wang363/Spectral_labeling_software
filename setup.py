from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "models.py",
        compiler_directives={
            "language_level": "3"
        }
    )
)
