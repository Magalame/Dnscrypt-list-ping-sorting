# Dnscrypt-list-ping-sorting
A program to ping and sort the DNS servers proposed by dnscrypt, see here: https://dnscrypt.org

The script pings five times each server, and displays the average and the error on the mean and the reliablity. The final display lists all the servers that responded by their ping.

It's written in python3 and (unfortunately) needs root privileges because of the ping function that requires creating sockets. 

The ping function is from there: https://gist.github.com/pyos/10980172

# How to use it?
The most straightforward way is simply to go with:

`wget https://raw.githubusercontent.com/LawLawL/Dnscrypt-list-ping-sorting/master/ping_dnscrypt.py`

then

`sudo python3 ping_dnscrypt.py`