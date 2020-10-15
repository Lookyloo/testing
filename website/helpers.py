#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import os


def get_homedir() -> Path:
    if not os.environ.get('LOOKYLOO_TESTING_HOME'):
        # Try to open a .env file in the home directory if it exists.
        if (Path(__file__).resolve().parent / '.env').exists():
            with (Path(__file__).resolve().parent / '.env').open() as f:
                for line in f:
                    key, value = line.strip().split('=', 1)
                    if value[0] in ['"', "'"]:
                        value = value[1:-1]
                    os.environ[key] = value

    if not os.environ.get('LOOKYLOO_TESTING_HOME'):
        guessed_home = Path(__file__).resolve().parent
        raise Exception(f"LOOKYLOO_TESTING_HOME is missing. \
Run the following command (assuming you run the code from the clonned repository):\
    export LOOKYLOO_TESTING_HOME='{guessed_home}'")
    return Path(os.environ['LOOKYLOO_TESTING_HOME'])
