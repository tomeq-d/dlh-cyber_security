#!/bin/bash
whois $1 | awk 'BEGIN{s=""} /^Registrant /{s="Registrant"} /^Admin /{s="Admin"} /^Tech /{s="Tech"} s!="" && /: /{line=$0; gsub(/^[ \t]+/,"",line); n=index(line,": "); field=substr(line,1,n-1); val=substr(line,n+2); if(field~/Street/) val=val" "; if(field~/Phone Ext|Fax Ext/) printf "%s %s:,%s\n",s,field,val; else printf "%s %s,%s\n",s,field,val}' > $1.csv
