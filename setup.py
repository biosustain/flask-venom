import codecs

from setuptools import setup


setup(
    name='Flask-Venom',
    version='1.0.1',
    url='https://github.com/biosustain/flask-venom',
    license='MIT',
    author='Lars Schöning',
    author_email='lays@biosustain.dtu.dk',
    description='Flask extension for the Venom RPC framework',
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    py_modules=['flask_venom'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'venom'
    ],
    test_suite='nose.collector',
    tests_require=[
        'flask-testing'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)