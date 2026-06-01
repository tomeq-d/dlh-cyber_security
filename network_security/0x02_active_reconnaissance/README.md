ACTIVE RECONNAISSANCE


| Task | Description                                           |
|------|-------------------------------------------------------|
| 0    | Scan top ports with nmap, save open ports             |
| 1    | Edit /etc/hosts, identify web server name and version |
| 2    | Find flag 1 hidden in HTML source code comment        |
| 3    | Find the SQL-injectable endpoint                      |
| 4    | Use sqlmap to find database name and table count      |
| 5    | Dump Users table with sqlmap, extract flag 2          |
| 6    | Use gobuster to find hidden admin panel path          |
| 7    | Login to admin panel, extract flag 3                  |
