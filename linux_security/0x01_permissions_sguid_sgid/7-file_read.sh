#!/bin/bash
# Setting read-only permnission for others on all files and directories. I like it!
find "$1" -type f -exec chmod o=r {} \; 2>/dev/null
