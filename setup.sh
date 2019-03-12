#!/usr/bin/env bash -e
PYTHON=`which python3`
VENV=venv

if [ ! -e "./config.ini" ]
then
    cp config.ini.default config.ini
fi
if [ -f "$PYTHON" ]
then

    if [ ! -d $VENV ]
    then
        # Create a virtual environment if it doesn't exist.
        virtualenv $VENV -p python3
    else
        if [ -e $VENV/bin/python2 ]
        then
            # If a Python2 environment exists, delete it first
            # before creating a new Python 3 virtual environment.
            rm -r $VENV
            virtualenv $VENV -p python3
        fi
    fi

    source $VENV/bin/activate

    pip3 install -r requirements.txt
else
    >&2 echo "Cannot find Python 3. Please install it."
fi
