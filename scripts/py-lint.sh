#!/bin/bash

pylint mediawiki/

echo 'pylint status code:' $?

exit 0

# Will exit with status of last command.
