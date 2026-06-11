#!/bin/bash
ffuf -w DLH-wordlist.txt -u http://web0x04.hbtn -H "Host: FUZZ.web0x04.hbtn"
