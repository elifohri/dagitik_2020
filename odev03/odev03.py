import numpy as np
import matplotlib.pyplot as plt

f = open("lab8_3.87-4.18-1.57.mbd", "r")

timestamp = []
sensor_transmitter_pair = []
rssi = []
sorted_rssi = []
dict1 = {}
dict2 = {}
dict3 = {}
dict4 = {}

for line in f:
    splittedLine = line.strip().split(",")
    timestamp.append(splittedLine[0])
    sensor_transmitter_pair.append((splittedLine[1],splittedLine[2]))
    rssi.append(splittedLine[3])
    sorted_rssi.append(splittedLine[3])

#1. soru 
sorted_rssi.sort()
max = sorted_rssi[0]
min = sorted_rssi[-1]
range_set = int(max)-int(min)+1

j = 0
for i in sensor_transmitter_pair :
    if i in dict1 :
        x = rssi[j]
        x = abs(int(max)-int(x)) 
        dict1[i][(range_set)-x-1] += 1
    else :
        no_of_rssi = [0] * range_set
        dict1[i] = no_of_rssi
        x = rssi[j]
        x = abs(int(max)-int(x)) 
        dict1[i][(range_set)-x-1] += 1
    j += 1

x_1 = np.arange(int(min),int(max)+1)

#fig = plt.figure(figsize=(20,6))

z = 1
for i in dict1 :
    q = dict1[i]
    y_1 = np.array(q)
    plt.subplot(2, 4, z)
    plt.bar(x_1,y_1,width=0.9)
    plt.title(i, fontsize = 5)
    z += 1
    plt.tight_layout()
plt.show()

#2. soru
k = 0
for m in sensor_transmitter_pair :
    if m in dict2 :    
        dict2[m].append(timestamp[k])
    else :
       dict2[m] = [timestamp[k]]
    k += 1
    
for n in dict2 :
    dict3[n] = [0]
    p = 0
    while (p+100) < len(dict2[n]) :
        f = 100/(float(dict2[n][p+100])-float(dict2[n][p]))
        dict3[n].append(f)
        p += 1
    del dict3[n][0] 

z = 1
for i in dict3 :
    q = dict3[i]
    y_2 = np.array(q)
    x_2 = np.arange(0,len(y_2),1) 
    plt.subplot(2, 4, z)
    plt.plot(y_2)
    plt.title(i, fontsize = 5)
    z += 1
    plt.tight_layout()
plt.show()
        
#3. soru
for t in dict3 :
    freq_arr = [0] * 20
    w = 0
    while w < len(dict3[t]) :  
        if 1.5 <= dict3[t][w] < 1.55:
            freq_arr[0] += 1
        elif 1.55 <= dict3[t][w] < 1.6:
            freq_arr[1] += 1
        elif 1.6 <= dict3[t][w] < 1.65:
            freq_arr[2] += 1
        elif 1.65 <= dict3[t][w] < 1.7:
            freq_arr[3] += 1
        elif 1.7 <= dict3[t][w] < 1.75:
            freq_arr[4] += 1
        elif 1.75 <= dict3[t][w] < 1.8:
            freq_arr[5] += 1
        elif 1.8 <= dict3[t][w] < 1.85:
            freq_arr[6] += 1
        elif 1.85 <= dict3[t][w] < 1.9:
            freq_arr[7] += 1
        elif 1.9 <= dict3[t][w] < 1.95:
            freq_arr[8] += 1
        elif 1.95 <= dict3[t][w] < 2.0:
            freq_arr[9] += 1
        elif 2.0 <= dict3[t][w] < 2.05:
            freq_arr[10] += 1
        elif 2.05 <= dict3[t][w] < 2.1:
            freq_arr[11] += 1
        elif 2.10 <= dict3[t][w] < 2.15:
            freq_arr[12] += 1
        elif 2.15 <= dict3[t][w] < 2.2:
            freq_arr[13] += 1
        elif 2.2 <= dict3[t][w] < 2.25:
            freq_arr[14] += 1
        elif 2.25 <= dict3[t][w] < 2.3:
            freq_arr[15] += 1
        elif 2.3 <= dict3[t][w] < 2.35:
            freq_arr[16] += 1
        elif 2.35 <= dict3[t][w] < 2.4:
            freq_arr[17] += 1
        elif 2.4 <= dict3[t][w] < 2.45:
            freq_arr[18] += 1
        elif 2.45 <= dict3[t][w] < 2.5:
            freq_arr[19] += 1
        w += 1    
    dict4[t] = freq_arr
dict1

z = 1
for i in dict4 :
    q = dict4[i]
    y_3 = np.array(q)
    x_3 = np.arange(1.5,2.5,0.05)  
    print(x_3)
    print(y_3)
    plt.subplot(2, 4, z)
    plt.bar(x_3,y_3,width=0.05)
    plt.title(i, fontsize = 5)
    z += 1
    plt.tight_layout()
plt.show()
    
f.close()