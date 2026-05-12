# Mandatory Access Control project

## Project explores MAC in Linux. Focus on SELinux and AppArmor.

| File | Description |
|------|-------------|
| 0-analyse_mode.sh | Prints the current SELinux status/mode on the system |
| 1-security_match.sh | Displays the status of AppArmor security profiles on the system |
| 2-list_http.sh | Lists all SELinux ports filtered for HTTP services |
| 3-add_port.sh | Adds TCP port 81 as http_port_t in SELinux port management |
| 4-list_user.sh | Lists all SELinux user mappings with roles and MLS levels |
| 5-add_selinux.sh | Adds a new SELinux login mapping linking a Linux user to user_u |
| 6-list_booleans.sh | Lists all SELinux booleans with their current and default states |
| 7-set_sendmail.sh | Sets the SELinux boolean httpd_can_sendmail to on permanently |
