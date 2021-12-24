# ArkTracker

https://cathiesark.com/

https://www.arktrack.com/

## Install Python Packages
### Ubuntu
$ python3 -m pip install cx_Oracle --upgrade
Collecting cx_Oracle
  Downloading cx_Oracle-8.1.0-cp38-cp38-manylinux1_x86_64.whl (825 kB)
     |████████████████████████████████| 825 kB 8.3 MB/s 
Installing collected packages: cx-Oracle
Successfully installed cx-Oracle-8.1.0

apt-get install python3-dateutil python3-lxml

### Oracle Linux
dnf install oracle-release-el8
dnf install oracle-instantclient19.10-basiclite oracle-instantclient19.10-devel oracle-instantclient19.10-jdbc oracle-instantclient19.10-odbc oracle-instantclient19.10-sqlplus oracle-instantclient19.10-tools

rpm -i oracle-instantclient19.10-precomp-19.10.0.0.0-1.aarch64.rpm 


dnf install python39
dnf install python39-lxml python3-dateutil python39-requests
dnf install python39-pip python39-devel

python3.9 -m pip install cx_Oracle --upgrade
python3.9 -m pip install py_dateutil --upgrade

