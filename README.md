# Dnscrypt-list-ping-sorting
A program to ping and sort the DNS servers proposed by dnscrypt, see here: https://dnscrypt.org

The script pings five times each server, and displays the average and the error on the mean and the reliablity. The final display lists all the servers that responded, sorted by their ping time.

It's written in python3 and (unfortunately) needs root privileges because of the ping function that requires creating sockets. 

The ping function is from there: https://gist.github.com/pyos/10980172

# How to use it?
The most straightforward way is simply to go with:

`wget https://raw.githubusercontent.com/LawLawL/Dnscrypt-list-ping-sorting/master/ping_dnscrypt.py`

then

`sudo python3 ping_dnscrypt.py`

# You don't have python or the good version of python, and you want to download an executable?
You can download it here:https://drive.google.com/file/d/0Bxzq1JsVPF3eTFdFOTF6Wk9IbEk/view

Once downloaded and installed, you can launch it with typing
`"C:\Program Files\Ping dnscrypt\ping.exe"`
with the quotation signs.

# The display isn't great, some charac returns are missed
I don't know how to solve it yet, for now I strongly recommend you use it in full screen (not the F11 type of fullscren, just when you click on the square next to the cross at the top right corner of the terminal).
