#!/bin/bash
subfinder -d $1 -silent | awk -v d="$1" '{print; cmd="dig +short " $1 " | tail -n1"; cmd | getline ip; close(cmd); if(ip!="") print $1 "," ip >> d".txt"}'
