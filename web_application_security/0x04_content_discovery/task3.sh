#!/bin/bash
for word in $(cat dns_wordlist.txt);
	do 
#		echo "Trying $word"
		dig @web0x04.hbtn $word.db.web0x04.hbtn any +short | grep -i flag
	done
