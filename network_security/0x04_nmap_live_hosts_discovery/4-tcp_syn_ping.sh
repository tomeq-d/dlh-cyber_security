#!/bin/bash
nmap -sn -PS 22,80,443 $1
