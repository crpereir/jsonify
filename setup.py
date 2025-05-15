from setuptools import setup, find_packages

setup(
    name='jsonify', 
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
        'tqdm==4.67.1',
        'lxml',
        'pandas',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'jsonify=jsonify.main:main', 
        ],
    },
    author='Carolina Pereira',
    description='Convert files to JSON format',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/crpereir/jsonify', 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
