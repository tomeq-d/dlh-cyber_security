#!/bin/bash
echo "$1" | sed 's/^{xor}//' | base64 -d | perl -pe '$_^="_"x length'
