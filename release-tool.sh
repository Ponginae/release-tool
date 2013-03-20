#!/bin/bash
SHELL_PATH=`dirname "$0"`
#SHELL_PATH=`( cd "$MY_PATH" && pwd )`

if [[ $1 = "tool-setup" ]]; then
	virtualenv ./
	$SHELL_PATH/bin/pip install paver
	$SHELL_PATH/bin/pip install gitpython
else
	$SHELL_PATH/bin/paver -f $SHELL_PATH/pavement.py $*
fi
