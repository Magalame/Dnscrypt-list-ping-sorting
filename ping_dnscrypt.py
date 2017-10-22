import os
import csv
import time
import random
import struct
import select
import socket
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

#-------------------------------some useful functions for threading

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
      
   def run(self):
       
      global ipv6_available 
       
      self.ping_result = None #we set it to none in case the ping function fails, it spares a bit of error handling
      self.port_originally_none = False
      
      if self.port == None: #from the original function
          self.port = 53
          self.port_originally_none = True
      
      if not self.ipv6: #ipv4
            try:
                  self.ping_result = pingtcp(self.ip,int(self.port))
                  if self.ping_result == None:
                        if self.port_originally_none:
                              self.ping_result = pingtcp(self.ip,443)
                              if self.ping_result == None:
                                  self.ping_result = ping(self.ip)
                        else:
                              self.ping_result = ping(self.ip)
                  
            except:
                raise

      else: # no need to re-check if ipv6 is available, it cannot be called anyway if ipv6_available  is false
            try: #will need to implement a ipv6 implementation of the tcp ping
                  self.ping_result = ping(self.ip,ipv6=self.ipv6)
                  
            except:
                  raise


class meanPingThread (threading.Thread):
   def __init__(self, ip, row, nb_ping, port, ipv6=False):
      threading.Thread.__init__(self)
      self.ip = ip
      self.row = row
      self.nb_ping = nb_ping 
      self.port = port
      self.ipv6 = ipv6
      #self.terminal = sys.stdout
      
   def run(self):
      global liste
      global down_liste
      #global nb_ping
      
      try:
 #    sys.stdout.write("Pinging " + ip[0].split(':')[0] + "\r")
         #with self.lock:
         if self.ipv6: #ipv6
             ping_result = meanPing(self.ip,args.number_ping,int(self.port), True)
         else:
             ping_result = meanPing(self.ip[0].split(':')[0],args.number_ping,self.port) #le deuxieme paramètre est le nombre de ping
 
      except Exception as e:
         
         printt(str(e))
         
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
def ping(addr, timeout=1, number=1, data=b'', ipv6 = False):
    global ipv6_available
    try:
        if ipv6:
            
            socket_type = socket.AF_INET6
        else:
            socket_type = socket.AF_INET
            
        with socket.socket(socket_type, socket.SOCK_RAW, socket.IPPROTO_ICMP) as conn:
            a = random.randrange(0, 65536)
            payload = struct.pack('!HH', a, number) + data
            #executer(sys.stdout.write(str(a)+"\n"))
            
            if ipv6:
                conn.connect((addr, 80,0,0))
            else:
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
        return None
    except OSError:
        if ipv6:
            ipv6_available = False
        return None
    except:
        raise

def ping6(addr, timeout=1, number=1, data=b''):
    global ipv6_available
    try:
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
    except OSError:
        ipv6_available = False
        return None
        

def pingtcp(host, port): 

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
std_liste = [] #for debug purposes
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

    for thread in threadlist:
        thread.join()
        #with verrou:
        #    sys.stdout.write("[-] ip: " + addr +" thread:" + hex(id(thread))+"\n")

        if thread.ping_result != None:
            pinglist.append(thread.ping_result)
        else:
          #  print(down)
            down = down + 1

    pct_error = down/float(nb)
    
    if pct_error != 1:
        std_liste.append(std(pinglist)/(nb**0.5))
        return [mean(pinglist),std(pinglist)/(nb**0.5),down/nb]
    else:
        return [None,None,1.0]

ipv6_available = True #as not everyone has ipv6, we want to keep that somewhere
liste = [] #list of all servers that answered
down_liste = [] #list of all servers that do not answer
def pingDnscryptFile(filename):
    global ipv6_available
    
    global liste 
    liste = []
    
    global down_liste 
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

            if ip[0] != '': #if ipv4, because it is formatted a certain way in the csv file
                
                split_port = row[10].split(":")
                
                if len(split_port) == 2:
                    port = split_port[1]
                else:
                    port = None
                
                threadlist.append(meanPingThread(ip,row,args.number_ping, port))
                count_thread = count_thread+1
                threadlist[count_thread-1].start()
                time.sleep(args.server_delay)
                
                #threadlist[count_thread].join()
                #print(threadlist[count_thread].ip)

            elif ipv6_available: #if ipv6 and if ipv6 available
                #print(ip[1])
                port = ip[1].split("]")[1].split(':')[1]
                
                threadlist.append(meanPingThread(ip[1].split("]")[0],row,args.number_ping, port, True))
                count_thread = count_thread+1
                threadlist[count_thread-1].start()
                time.sleep(args.server_delay)

            else:
                #print("Ip not treated:",row[10])
                pass

            #sys.stdout.write("Number of servers pinged: %d   \r" % (count_row) )
    
    printt("----------------------Loading the result---------------------")
    
    for thread in threadlist:
        thread.join()
    print("---------------------Sorting the list-----------------------")
#    print(len(threadlist))
    mergeSort(liste)

    print("------------------------Merged list-------------------------")

    if ipv6_available: #as the length of the ip address is different and wil affect layout 
        print("Name \t\t\tIP address \t\t\t\tping \t\t reliability \tDNSSEC \tNo log \tLocation")
    else:
        print("Name \t\t\tIP address \t\tping \t\t reliability \tDNSSEC \tNo log \tLocation")
    
    for row in liste:

        if len(row[0])<8:a=3 #some computation so organize output
        elif len(row[0])<16:a=2
        else:a=1

        if ipv6_available:

            if len(row[10])<16:b=4 #same here, different computation because again different ip length with ipv6
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