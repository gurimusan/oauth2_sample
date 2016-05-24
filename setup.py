import os

from setuptools import setup, find_packages, Command

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = f.read().splitlines()

test_requires = [
    'pytest',
    'pytest-flake8',
    'pytest-cov',
    ]

development_requires = [
    'flake8',
    'pyramid-debugtoolbar',
    ] + test_requires


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pytest
        errno = pytest.main(['oauth2_sample'])
        raise SystemExit(errno)


setup(
    name='oauth2_sample',
    version='0.0',
    description='oauth2_sample',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        ],
    author='Nagatoshi Matsushita',
    author_email='gurimusan@gmail.com',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='oauth2_sample',
    install_requires=requires,
    tests_require=test_requires,
    extras_require={
        'dev': development_requires,
        'test': test_requires,
        },
    entry_points="""\
    [paste.app_factory]
    main = oauth2_sample:main
    [console_scripts]
    initialize_oauth2_sample_db = oauth2_sample.scripts.initializedb:main
    """,
    )
