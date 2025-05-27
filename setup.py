from setuptools import setup, find_packages

setup(
    name='jsonify',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
)
