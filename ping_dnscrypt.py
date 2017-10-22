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
import argparse
from timeit import default_timer as timer

#-----------------------------------parsing of arguments
parser = argparse.ArgumentParser()

parser.add_argument("-n", "--number_ping", type=int, help="sets the number of times a server is pinged")
parser.add_argument("-p", "--ping_delay", type=float, help="sets delay between each ping")
parser.add_argument("-s", "--server_delay", type=float, help="sets delay between pinging of each server")

args = parser.parse_args()

if not args.ping_delay:
    args.ping_delay = 0.01

if not args.server_delay:
    args.server_delay = 0.1

if not args.number_ping:
    args.number_ping = 50

"""print(args.ping_delay)
print(args.server_delay)
print(args.number_ping)"""
#-------------------------------some useful functions 

start_time = time.time()
verrou = threading.Lock()

def printt(msg):
    with verrou:
        sys.stdout.write(msg+"\n")
        
def executer(task):
    with verrou:
        task
        
#---------------------------------------

class PingThread (threading.Thread):
   def __init__(self, ip, port, ipv6):
      threading.Thread.__init__(self)
      self.ip = ip
      self.port = port
      self.ipv6 = ipv6
   #   self.terminal = sys.stdout
    #  self.lock = threading.Lock()
      
   def run(self):
      self.ping_result = None
   #   global pinglist
    #  global down
    #  with self.lock:
     #     self.terminal.write(hex(id(self.ip))+"\n")
      global ipv6_available
      
      if not self.ipv6:
            try:
                  self.ping_result = pingtcp(self.ip,self.port)
                  
                  if self.ping_result == None:
                        self.ping_result = ping(self.ip)
       #                 printt("------------------------pass")                        
                  
            except Exception as e:
                raise
                printt(str(e))
            #print(self.ping_result)
      else:
            try:
                  self.ping_result = ping6(self.ip)
                  
            except Exception as e:
#                  print("#################################################")
                  raise
                  if str(e) == "[Errno 101] Network is unreachable":
                        ipv6_available = False
#                        print("sucess")
#                  print("#################################################")
                  
            #ping_result = ping6(self.ip)
      #print(ping_result)
      #pas de valeur return ou quoi que ce soit, parce qu'on le récupèrera de l'extérieur
      """if self.ping_result != None:
            pinglist.append(self.ping_result)
      else:
            down = down + 1"""
#nb_ping = 50
class meanPingThread (threading.Thread):
   def __init__(self, ip, row, nb_ping, port):
      threading.Thread.__init__(self)
      self.ip = ip
      self.row = row
      self.nb_ping = nb_ping
      self.port = port
      #self.terminal = sys.stdout
      
   def run(self):
      global liste
      global down_liste
      #global nb_ping
      
      if self.port == None:
          self.port = 53
      
      try:
 #    sys.stdout.write("Pinging " + ip[0].split(':')[0] + "\r")
         #with self.lock:
         ping_result = meanPing(self.ip[0].split(':')[0],args.number_ping,int(self.port)) #le deuxieme paramètre est le nombre de ping
 
      except Exception as e:
         
         printt(e)
         
         ping_result = [None]
         
      if ping_result[0] != None:

         self.row.append(ping_result[0])
         self.row.append(ping_result[1])
         self.row.append(ping_result[2])
         liste.append(self.row)

      else:
         down_liste.append(self.row)
         
#-------------------------------------some statistical functions

def mean(list):
    try:
        return sum(list) / len(list)
    except ZeroDivisionError:
        return None

def std(list):
    mean_var = mean(list)
    variance = sum([(x-mean_var)**2 for x in list]) / len(list)
    return variance**0.5

#---------------------------------base ping function

def chk(data):
    x = sum(x << 8 if i % 2 else x for i, x in enumerate(data)) & 0xFFFFFFFF
    x = (x >> 16) + (x & 0xFFFF)
    x = (x >> 16) + (x & 0xFFFF)
    return struct.pack('<H', ~x & 0xFFFF)

# from https://gist.github.com/pyos/10980172
def ping(addr, timeout=1, number=1, data=b''):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
            a = random.randrange(0, 65536)
            payload = struct.pack('!HH', a, number) + data
            #executer(sys.stdout.write(str(a)+"\n"))
            
            conn.connect((addr, 80))
            conn.sendall(b'\x08\0' + chk(b'\x08\0\0\0' + payload) + payload)
            start = time.time()

            while select.select([conn], [], [], max(0, start + timeout - time.time()))[0]:
                data = conn.recv(65536)
                if len(data) < 20 or len(data) < struct.unpack_from('!xxH', data)[0]:
                    continue
                if data[20:] == b'\0\0' + chk(b'\0\0\0\0' + payload) + payload:
                    return time.time() - start
    except socket.gaierror: #happens when it is totally not accessible
        pass 
    except Exception as e:
        raise
        printt(str(e))

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

def pingtcp(host, port): 
    count=1
    s_runtime = None

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        time.sleep(1)
                
        start_time = timer()
                
        s.connect((host, port))
        s.shutdown(socket.SHUT_RD)
                
        stop_time = timer()
                                
                
        s_runtime = (stop_time-start_time)
            
        return s_runtime
    except ConnectionRefusedError: #tcp port unaccessible
        pass
    except TimeoutError: #self explanatory
        pass
    except OSError:
        pass          #we skip all these errors because there will be the second try anyway
    except Exception as e:
        raise
        printt(str(e))
            
#--------------------------------merge sort algorithm

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
        
#-------------------------------

#pinglist = []
#down = 0
std_liste = []
#time_to_sleep = 0.1
def meanPing(addr,nb,port,ipv6=False):
 #   global pinglist
    global std_liste
    pinglist = []

  #  global down
    down = 0

    threadlist = []

    for i in range(0,nb):

        time.sleep(args.ping_delay) #we add this little delay otherwise we might make the network saturate and give us wrong data
        threadlist.append(PingThread(addr,port,ipv6))
        threadlist[i].start()
        #with verrou:
            #sys.stdout.write("[+] ip: " + addr +" thread:" + hex(id(threadlist[i]))+"\n")
            
#        print(str(i) + " " + str(ping_result))

    for thread in threadlist:
        thread.join()
        #with verrou:
        #    sys.stdout.write("[-] ip: " + addr +" thread:" + hex(id(thread))+"\n")
        #print("thread result: "+str(thread.ping_result))
        #print("length of thread:" + str(len(threadlist)))
        if thread.ping_result != None:
            pinglist.append(thread.ping_result)
        else:
          #  print(down)
            down = down + 1
        
    """for thread in threadlist:
        print("thread result: "+str(thread.ping_result))
        print("length of thread:" + str(len(threadlist)))
        if thread.ping_result != None:
            pinglist.append(thread.ping_result)
        else:
          #  print(down)
            down = down + 1"""
    #print(str(id(pinglist))+"\n")
    #print("ip:",addr,"liste:",pinglist)
    #executer(print(pinglist))
    pct_error = down/float(nb)
    
    
    
    if pct_error != 1:
        std_liste.append(std(pinglist)/(nb**0.5))
        return [mean(pinglist),std(pinglist)/(nb**0.5),down/nb]
    else:
        return [None,None,1.0]

ipv6_available = True
liste = []
down_liste = []
def pingDnscryptFile(filename):
    global ipv6_available
    
    global liste #liste des serveurs ayant répondu
    liste = []
    
    global down_liste #liste des serveurs n'ayant pas répondu
    down_liste = []
    
    count_row = 0
    count_thread = 0 #pour suivre le nombre de thread vraiment commencés qui est different du nombre de row
    
    threadlist = [] #avoir la liste des threads pour les gérer
    
    reader = csv.reader(open(filename, "rt"), delimiter=",")
#    ipv6_available = True
    print("-----------------------Pinging servers-----------------------")
    for row in reader:
        if row[0] != "Name":
            count_row = count_row + 1

            ip = row[10].split("[")

            if ip[0] != '': #if ipv4
                
                #print("ip: ", ip[0])
                
                split_port = row[10].split(":")
                
                if len(split_port) == 2:
                    port = split_port[1]
                else:
                    port = None
                
                threadlist.append(meanPingThread(ip,row,args.number_ping, port))
                threadlist[count_thread].start()
                time.sleep(args.server_delay)
                
                #threadlist[count_thread].join()
                #print(threadlist[count_thread].ip)
                count_thread = count_thread+1
                """try:
 #                   sys.stdout.write("Pinging " + ip[0].split(':')[0] + "\r")
                    ping_result = meanPing(ip[0].split(':')[0],50)
                except:
                    ping_result = [None]"""
                

            elif ipv6_available: #not yet threaderized

                try:
#                    sys.stdout.write("Pinging " + ip[1].split("]")[0] + "\r")
                    #print("ipv6: "+ping_result)
                    ping_result = meanPing(ip[1].split("]")[0],1,1)
                    #print("ipv6: "+ping_result)
                except Exception as e:
 #                   print("say hi")
  #                  print("--------------------------------------------------")
                    print(str(e))
    #                print("--------------------------------------------------")
                    if str(e) == "[Errno 101] Network is unreachable":
                        ipv6_available = False

                    ping_result = [None]
                    
                if ping_result[0] != None:

                    row.append(ping_result[0])
                    row.append(ping_result[1])
                    row.append(ping_result[2])
                    liste.append(row)

                else:
                    down_liste.append(row)

            else:
                ping_result = [None]

            

            sys.stdout.write("Number of servers pinged: %d   \r" % (count_row) )
    
    printt("--------------------Loading the result----------------------")
    
    for thread in threadlist:
        thread.join()
    print("---------------------Sorting the list-----------------------")
#    print(len(threadlist))
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
        
    #print("Moyenne std:",round(mean(std_liste)*1000,3))
    #print("Delais =",args.ping_delay,args.server_delay,"\nNb ping:",args.number_ping)


def pingDnscrypt():

    if not os.path.isfile("dnscrypt-resolvers.csv"):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/jedisct1/dnscrypt-proxy/master/dnscrypt-resolvers.csv","dnscrypt-resolvers.csv")
    pingDnscryptFile("dnscrypt-resolvers.csv")


if __name__ == '__main__':
    pingDnscrypt()

#print("--- %s seconds ---" % (time.time() - start_time))