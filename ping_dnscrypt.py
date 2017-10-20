import os
import csv
import time
import random
import struct
import select
import socket
#import numpy as np
#import math
import sys
import urllib.request
import threading
from timeit import default_timer as timer
start_time = time.time()

def mean(list): 
    return sum(list) / len(list)

def std(list):
    mean_var = mean(list)
    variance = sum([(x-mean_var)**2 for x in list]) / len(list)
    return variance**0.5

def chk(data):
    x = sum(x << 8 if i % 2 else x for i, x in enumerate(data)) & 0xFFFFFFFF
    x = (x >> 16) + (x & 0xFFFF)
    x = (x >> 16) + (x & 0xFFFF)
    return struct.pack('<H', ~x & 0xFFFF)

# from https://gist.github.com/pyos/10980172
# ICMP ping for ipv4
def ping(addr, timeout=1, number=1, data=b''):
    with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
        payload = struct.pack('!HH', random.randrange(0, 65536), number) + data

        conn.connect((addr, 80))
        conn.sendall(b'\x08\0' + chk(b'\x08\0\0\0' + payload) + payload)
        start = time.time()

        while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
            data = conn.recv(65536)
            if len(data) < 20 or len(data) < struct.unpack_from('!xxH', data)[0]:
                continue
            if data[20:] == b'\0\0' + chk(b'\0\0\0\0' + payload) + payload:
                return time.time() - start
#ICMP ping for ipv6
def ping6(addr, timeout=1, number=1, data=b''):
    with socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
        payload = struct.pack('!HH', random.randrange(0, 65536), number) + data

        conn.connect((addr, 80,0,0))
        conn.sendall(b'\x08\0' + chk(b'\x08\0\0\0' + payload) + payload)
        start = time.time()

        while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
            data = conn.recv(65536)
            if len(data) < 20 or len(data) < struct.unpack_from('!xxH', data)[0]:
                continue
            if data[20:] == b'\0\0' + chk(b'\0\0\0\0' + payload) + payload:
                return time.time() - start
#TCP ping for ipv4, useful when ICMP is disabled on the pinged server
def pingtcp(host, port, count=1): 
    for n in range(1, count + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            time.sleep(1)
                
            start_time = timer()
                
            s.connect((host, port))
            s.shutdown(socket.SHUT_RD)
                
            stop_time = timer()
                                
                
            s_runtime = 1000 * (stop_time-start_time)
            
            return s_runtime

        except Exception as e:
            print(e)

def merge(list,left,right):

    i=j=0

    while i < len(left) and j < len(right):
        if left[i][14] < right[j][14]:
            list[i+j]=left[i]
            i=i+1
        else:
            list[i+j]=right[j]
            j=j+1

    while i < len(left):
        list[i+j]=left[i]
        i=i+1

    while j < len(right):
        list[i+j]=right[j]
        j=j+1

def mergeSort(list):

    if len(list)>1:
        half = len(list)//2
        left = list[:half]
        right = list[half:]

        mergeSort(left)
        mergeSort(right)

        merge(list,left,right)
        
class PingThread (threading.Thread):
   def __init__(self, ip, ipv6):
      threading.Thread.__init__(self)
      self.ip = ip
      self.ipv6 = ipv6
      
   def run(self):

      global ipv6_available
      if not self.ipv6:
            self.ping_result = ping(self.ip)
      else:
            try:
                  self.ping_result = ping6(self.ip)
            except Exception as e:
#                  print("#################################################")
#                  print(str(e))
                  if str(e) == "[Errno 101] Network is unreachable":
                        ipv6_available = False
#                        print("sucess")
#                  print("#################################################")
                  #return
            #ping_result = ping6(self.ip)
      #print(ping_result)


#pinglist = []
#down = 0
def meanPing(addr,nb,ipv6=False):
    #global pinglist
    pinglist = []

    #global down
    down = 0

    threadlist = []

    for i in range(0,nb):
        threadlist.append(PingThread(addr,ipv6))
        threadlist[i].start()
#        print(str(i) + " " + str(ping_result))

    for thread in threadlist:
        thread.join()
        
        if thread.ping_result != None:
            pinglist.append(thread.ping_result)
        else:
            down = down + 1

    pct_error = down/float(nb)
    #print("ip:",addr,"liste:",pinglist)
    if pct_error != 1:
        return [mean(pinglist),std(pinglist)/(nb**0.5),down/nb]
    else:
        return [None,None,1.0]

ipv6_available = True
def pingDnscryptFile(filename):
    global ipv6_available
    reader = csv.reader(open(filename, "rt"), delimiter=",")
    liste = []
    down_liste = []
    count = 0
#    ipv6_available = True
    print("-----------------------Pinging servers-----------------------")
    for row in reader:
        if row[0] != "Name":
            count = count + 1

            ip = row[10].split("[")

            if ip[0] != '': #if ipv4

                try:
 #                   sys.stdout.write("Pinging " + ip[0].split(':')[0] + "\r")
                    ping_result = meanPing(ip[0].split(':')[0],50)
                except:
                    ping_result = [None]

            elif ipv6_available:

                try:
#                    sys.stdout.write("Pinging " + ip[1].split("]")[0] + "\r")
                    ping_result = meanPing(ip[1].split("]")[0],50,1)
                except Exception as e:
 #                   print("say hi")
  #                  print("--------------------------------------------------")
   #                 print(str(e))
    #                print("--------------------------------------------------")
                    if str(e) == "[Errno 101] Network is unreachable":
                        ipv6_available = False

                    ping_result = [None]

            else:
                ping_result = [None]

            if ping_result[0] != None:

                row.append(ping_result[0])
                row.append(ping_result[1])
                row.append(ping_result[2])
                liste.append(row)

            else:
                down_liste.append(row)

            sys.stdout.write("Number of servers pinged: %d   \r" % (count) )

    print("---------------------Sorting the list-----------------------")

    mergeSort(liste)

    print("------------------------Merged list-------------------------")

    if ipv6_available:
        print("Name \t\t\tIP address \t\t\t\tping \t\t reliability \tDNSSEC \tNo log \tLocation")
    else:
        print("Name \t\t\tIP address \t\tping \t\t reliability \tDNSSEC \tNo log \tLocation")

    for row in liste:

        if len(row[0])<8:a=3
        elif len(row[0])<16:a=2
        else:a=1

        if ipv6_available:

            if len(row[10])<16:b=4
            elif len(row[10])<24:b=3
            elif len(row[10])<32:b=2
            else:b=1
        else:
            if len(row[10])<16:b=2
            else:b=1

        print(row[0] + a*"\t" + row[10] + b*"\t" + str(round(row[14]*1000,2)) + "\t" + "+/-" + str(round(row[15]*1000,2)) + "ms" + "\t"  + str(round(100-row[16]*100,1)) + "%" + "\t" + row[7] + "\t" + row[8] + "\t" + row[3])


def pingDnscrypt():

    if not os.path.isfile("dnscrypt-resolvers.csv"):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/jedisct1/dnscrypt-proxy/master/dnscrypt-resolvers.csv","dnscrypt-resolvers.csv")
    pingDnscryptFile("dnscrypt-resolvers.csv")


if __name__ == '__main__':
    pingDnscrypt()
#print("--- %s seconds ---" % (time.time() - start_time))