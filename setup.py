from setuptools import setup, find_packages

setup(
    name='jsonify',
    version='0.2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    description='A package to convert various file formats to JSON',
    author='Carol',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/jsonify',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.8',
    install_requires=[
        'lxml>=4.9.0',
        'pandas>=2.0.0',
    ],
)
