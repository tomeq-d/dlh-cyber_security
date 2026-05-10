#!/bin/bash
# Create group, change file ownership to it and sets permissions
addgroup "$1"
chgrp "$1" "$2"; chmod g+rx "$2"
