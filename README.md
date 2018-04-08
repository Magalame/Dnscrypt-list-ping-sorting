# Dnscrypt-list-ping-sorting
A program to ping and sort the DNS servers proposed by dnscrypt, see here: https://dnscrypt.info/

The script pings 5 times each server, and displays the average and the error on the mean and the reliablity. The final display lists all the servers that responded, sorted by their ping time.

It's written in python3 and (unfortunately) needs root privileges because of the ping function that requires creating sockets. 

The ping function is from there: https://gist.github.com/pyos/10980172

# How to use it?
The most straightforward way is simply to go with:

`wget https://raw.githubusercontent.com/LawLawL/Dnscrypt-list-ping-sorting/master/ping_dnscrypt.py`

then

`sudo python3 ping_dnscrypt.py`

If you think it goes too slowly you can increase the speed by using threading (although it might make the data less reliable, use it only if you're in a rush):

`sudo python3 ping_dnscrypt.py -t`

The default number of ping per server is 5 without threading, 10 with. You can specify the number if you want to change that (for example if you want to increase the precision of the 'reliability' parameter):

`sudo python3 ping_dnscrypt.py -n yournumberhere`

Although if you increase this number too much with the threading activated you might overload your network, and you will end up with inaccurate results. To avoid that you can define delay between every single ping request, the default is 0.02 seconds:

`sudo python3 ping_dnscrypt.py -p yourdelayinsecondshere`

You can also define a delay between each time we start pinging a server (as the program goes through a list), the default is 0.2 seconds:

`sudo python3 ping_dnscrypt.py -s yourdelayinsecondshere`



# You don't have python or the good version of python, and you want to download an executable (Windows)?
Portable version: https://drive.google.com/file/d/1o3ndcbgBnt4d_ErJ64FXeKWJMU3cgvK-/view?usp=sharing

And for 32 bits: https://drive.google.com/open?id=1aDX-0h7k9nAIBg0lFi5961_kjKOa7vPw

Once downloaded, find where is located 'pingdnscrypt.exe', then run open a terminal and type

`ping_dnscrypt.exe`

# It might happen that the display isn't great, some charac returns are missed sometimes
I don't know how to solve it yet, for now I strongly recommend you use it in full screen (not the F11 type of fullscren, just when you click on the square next to the cross at the top right corner of the terminal).
