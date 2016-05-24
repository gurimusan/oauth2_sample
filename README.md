oauth2_sample README
====================

Getting Started
---------------

    $ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    $ git clone https://github.com/yyuu/pyenv-virtualenv.git ~/.pyenv/plugins/pyenv-virtualenv
    $ cd <directory containing this file>
    $ cat .python-version
    $ pyenv install 3.4.3
    $ pyenv install 3.5.1
    $ pyenv virtualenv 3.4.3 oauth2_sample_py34
    $ pyenv virtualenv 3.5.1 oauth2_sample_py35
    $ python setup.py develop
    $ initialize_oauth2_sample_db development.ini
    $ pserve development.ini
