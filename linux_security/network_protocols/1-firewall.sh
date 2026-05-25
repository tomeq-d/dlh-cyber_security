#!/bin/bash
sudo iptables -A INPUT -s $1 -p tcp ! --dport 22 -j DROP
