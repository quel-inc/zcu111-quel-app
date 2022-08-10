import csv
import numpy as np
import math
import pprint
from matplotlib import pyplot as pyp
from scipy.fftpack import fft, fftshift, fftfreq
from scipy.signal import find_peaks
import pandas as pd

#Sampling Frequency (245.76*N/M)
#Fs = 3932.160
Fs = 6389.76
#Fs = 6512.64

#Goal Frequency
print("Output Frequency in [MHz]: ")
Fg = int(input())
#Center Frequency generated
CFg = 0
#Center Frequency samples
S = 0
#samples time distance
st = 1000/Fs
#waveform(0:sin,1:sawtooth,2:square,else:triangle)
print("Waveform(0:sine, 1:sawtooth, 2: square, 3:triangle): ")
waveform = input()

#Samples array[that return Fg exactly]
Sarr = np.zeros(256)
v = 0
#Best S value for Fg
for samples in range(1024,32768,32):
    CFbase = Fs/samples
    CF1 = int(Fg/CFbase)*CFbase
    CF2 = (int(Fg/CFbase)+1)*CFbase
    if abs(CF1-Fg) <= 0.01 :
        Sarr[v] = samples
        v+=1
    if abs(CF1 - Fg) < abs(CF2 - Fg):
        if abs(CF1-Fg) < abs(CFg-Fg):
            CFg = CF1
            S = samples
    else:
        if abs(CF2-Fg) < abs(CFg-Fg):
            CFg = CF2
            S = samples
print(Fg,CFg,S)

#Best S value for sawtooth
if waveform == "1":
    start_avg = np.zeros(int((32768-1024)/32))
    start_var = np.zeros(int((32768-1024)/32))
    peak_avg = np.zeros(int((32768-1024)/32))
    peak_var = np.zeros(int((32768-1024)/32))
    avg_diff = np.zeros(int((32768-1024)/32))
    opt_f = np.zeros(int((32768-1024)/32))
    v = 0
    while (Sarr[v] != 0):
        samples = int(Sarr[v])
        #print(v)
        counts = 0
        w = np.zeros(samples)
        for i in range(samples):
            w[i] = (i%(Fs/Fg))/(Fs/Fg)*2 -1
        for i in range(samples-1):
            if w[i] > w[i+1]:
                counts += 1
        start = np.zeros(counts)
        peak = np.zeros(counts)
        threshold = np.zeros(2*(counts+1))
        th = 0
        even = 0
        for i in range(1,samples):
            if w[i] >=0 and even == 0:
                if abs(w[i]) <= abs(w[i-1]):
                    threshold[th] = i
                else:
                    threshold[th] = i-1
                th += 1
                even = 1
            if w[i] <= 0 and even ==1:
                if abs(w[i]) <= abs(w[i-1]):
                    threshold[th] = i
                else:
                    threshold[th] = i-1
                th += 1
                even = 0
        start[0] = 0
        peak[0] = 0
        th = 0
        even = 0
        for i in range(samples-1):
            if i > threshold[th] and even==0:
                if w[i+1] < w[i]: 
                    peak[int(th/2)] = i
                    th+= 1
                    even = 1
            if i > threshold[th] and even==1:
                if abs(w[i]) >= abs(w[i+1]): 
                    start[int(th/2)] = i
                    even = 0
                    th+=1
        samp = int((samples-1024)/32)
        for i in range(counts):
            start_avg[samp] += w[int(start[i])]
            peak_avg[samp] += w[int(peak[i])]
        start_avg[samp] = start_avg[samp]/counts
        peak_avg[samp] = peak_avg[samp]/counts
        avg_diff[samp] = peak_avg[samp] - start_avg[samp]
        for i in range(counts):
            start_var += (w[int(start[i])] - start_avg[samp])**2
            peak_var += (w[int(peak[i])] - peak_avg[samp])**2
        start_var[samp] = start_var[samp]/counts
        peak_var[samp] = peak_var[samp]/counts
        #print("Start Average:",start_avg[samp],"Start Variance:",start_var[samp])
        #print("Peak Average:",peak_avg[samp],"Peak Variance:",peak_var[samp])
        #print("Average Difference:",avg_diff[samp])
        v+=1

    for i in range(int((32768-1024)/32)):
        opt_f[i] = (avg_diff[i] + 1/peak_var[i] + 1/start_var[i])
    max_avg = max(avg_diff)
    min_peak_var = min(peak_var)
    min_start_var = min(start_var)
    max_opt = max(opt_f)
    print("Max Average Difference",np.where(avg_diff == max_avg), max_avg)
    print("Min Peak Variance",np.where(peak_var == min_peak_var), min_peak_var)
    print("Min Start Variance",np.where(start_var == min_start_var), min_start_var)
    #print("Optimization",np.where(opt_f == max_opt), max_opt)
    print("Optimization",np.where(opt_f == max_opt), max_opt)
    #Samples number with max average difference
    S = (np.where(opt_f == max_opt)[0]*32)+1024

# Best S value for Square wave
if waveform == "2":
    counting_diff = np.ones(int((32768-1024)/32))
    n_avg = np.ones(int((32768-1024)/32))
    n_var = np.ones(int((32768-1024)/32))
    v = 0
    while (Sarr[v] != 0):
        samples = int(Sarr[v])
        #print(v)
        w = np.zeros(samples)
        for i in range(samples):
            if math.sin(2*math.pi*i*(Fg/Fs))>=0: w[i] = 1
            else: w[i] = 0
        up = np.count_nonzero( w== 1)
        down = np.count_nonzero( w==0)
        samp = int((samples-1024)/32)
        counting_diff[samp] = abs(up - down)
        ndiff = np.diff(np.r_[0,np.flatnonzero(np.diff(w))+2,w.size])
        for i in range(int(ndiff.size)):
            n_avg[samp] += ndiff[i]
        n_avg[samp] = n_avg[samp]/(ndiff.size)
        for i in range(int(ndiff.size)):
            n_var[samp] += (ndiff[i] - n_avg[samp])**2
        n_var[samp] = n_var[samp]/(ndiff.size)
        v+=1


    min_cd = min(counting_diff)
    min_nv = min(n_var)
    print("Min Counting Difference", np.where(counting_diff == min_cd), min_cd)
    print("Min Counting Variation", np.where(n_var == min_nv), min_nv)
    #Samples number with min counting variation
    S = (np.where(n_var == min_nv)[0]*32)+1024


# Best S value for Triangle wave
if waveform == "3":
    start_avg = np.zeros(int((32768-1024)/32))
    start_var = np.zeros(int((32768-1024)/32))
    peak_avg = np.zeros(int((32768-1024)/32))
    peak_var = np.zeros(int((32768-1024)/32))
    avg_diff = np.zeros(int((32768-1024)/32))
    avg_pd= np.zeros(int((32768-1024)/32))
    var_pd = np.ones(int((32768-1024)/32))
    v = 0
    while (Sarr[v] != 0):
        samples = int(Sarr[v])
        counts = 0
        w = np.zeros(samples)
        for i in range(samples):
            w[i] = ((Fs/(2*Fg))-abs((Fs/(2*Fg))-i%(Fs/Fg)))/(Fs/(2*Fg))
        for i in range(samples-1):
            if w[i] > w[i+1]:
                counts += 1
        start = np.zeros(counts)
        peak = np.zeros(counts)
        dis_to_peak = np.zeros([counts,2])
        threshold = np.zeros(2*(counts+1))
        th = 0
        even = 0
        for i in range(1,samples):
            if w[i] >=0 and even == 0:
                if abs(w[i]) <= abs(w[i-1]):
                    threshold[th] = i
                else:
                    threshold[th] = i-1
                th += 1
                even = 1
            if w[i] <= 0 and even ==1:
                if abs(w[i]) <= abs(w[i-1]):
                    threshold[th] = i
                else:
                    threshold[th] = i-1
                th += 1
                even = 0
        start[0] = 0
        peak[0] = 0
        th = 0
        even = 0
        for i in range(samples-1):
            if i > threshold[th] and even==0:
                if w[i+1] < w[i]: 
                    peak[int(th/2)] = i
                    th+= 1
                    even = 1
            if i > threshold[th] and even==1:
                if abs(w[i]) >= abs(w[i+1]): 
                    start[int(th/2)] = i
                    even = 0
                    th+=1
        for i in range(peak.size-1):
            dis_to_peak[i][0] = peak[i]-start[i]
            dis_to_peak[i][1] = start[i+1]-peak[i]
        samp = int((samples-1024)/32)
        for i in range(counts):
            start_avg[samp] += w[int(start[i])]
            peak_avg[samp] += w[int(peak[i])]
        start_avg[samp] = start_avg[samp]/counts
        peak_avg[samp] = peak_avg[samp]/counts
        avg_diff[samp] = peak_avg[samp] - start_avg[samp]
        for i in range(counts):
            start_var += (w[int(start[i])] - start_avg[samp])**2
            peak_var += (w[int(peak[i])] - peak_avg[samp])**2
        start_var[samp] = start_var[samp]/counts
        peak_var[samp] = peak_var[samp]/counts

        for i in range(int(peak.size)):
            avg_pd[samp] += dis_to_peak[i][0]+dis_to_peak[i][1]
        avg_pd[samp] = avg_pd[samp]/(2*peak.size)

        for i in range(int(peak.size)):
            var_pd[samp] += (dis_to_peak[i][0] - avg_pd[samp])**2
        var_pd[samp] = var_pd[samp]/(peak.size)
        #print("Start Average:",start_avg[samp],"Start Variance:",start_var[samp])
        #print("Peak Average:",peak_avg[samp],"Peak Variance:",peak_var[samp])
        #print("Average Difference:",avg_diff[samp])
        v+=1

    max_avg = max(avg_diff)
    min_peak_var = min(peak_var)
    min_start_var = min(start_var)
    min_pd_var = min(var_pd)
    print("Max Average Difference",np.where(avg_diff == max_avg), max_avg)
    print("Min Peak Variance",np.where(peak_var == min_peak_var), min_peak_var)
    print("Min Start Variance",np.where(start_var == min_start_var), min_start_var)
    print("Min Distance to Peak Variation",np.where(var_pd == min_pd_var), min_pd_var)

    #Samples number with max average difference
    S = (np.where(var_pd == min_pd_var)[0]*32)+1024
S = 1024
print("Best Samples:",S)
#waveform data
w = np.zeros(S, dtype=np.float32)

for i in range(int(S)):
    if waveform == "0":
        #sine
        w[i] = math.sin(2*math.pi*i*(Fg/Fs))
    elif waveform =="1":
        #sawtooth
        #w[i] = (i%(Fs/Fg))/(Fs/Fg)*2 -1
        w[i] = ((Fs/Fg)-i%(Fs/Fg))/(Fs/Fg)*2 -1
    elif waveform =="2":
        #square
        if math.sin(2*math.pi*i*(Fg/Fs))>=0: w[i] = 1
        else: w[i] = -1
        #w[i]=np.sign(math.sin(2*math.pi*i*(Fg/Fs)))
    else:
        #triangle
        w[i] = ((Fs/(2*Fg))-abs((Fs/(2*Fg))-i%(Fs/Fg)))/(Fs/(2*Fg))

#Waveform distortion

reg = 0
for i in range(int(S)):
    if waveform == "1":
        if i <1:
            reg+=1
        if i>=1:
            if w[i] <= 0.995:
                reg+=1
            else:
                break
    if waveform == "2":
        if w[i] == 1:
            reg += 1
        else:
            break
print("reg:",reg)


par = 0
#w[0] = 0.8
if waveform == "1":
    w[0] = 2.1
if waveform == "2":
    w[0] = 1.275
for i in range(1,int(S)):
    
    if waveform == "1":
        if i%reg==0:
            par = 0
        else:
            par += 1
            #final adjust
        if par < reg/128: #2(0,1)
            w[i] = 2.1
        elif par >= reg/128 and par < reg/64: #2(0,1)
            w[i] = 1.8
        elif par >= reg/64 and par < reg/48: #2(2,3)
            w[i] = 2.2
        elif par >= reg/48 and par < reg/32: #2(2,3)
            w[i] = 1.8
        elif par >= reg/32 and par < reg/24: #2(4,5)
            w[i] = 1.6
        elif par >= reg/24 and par < reg/20: #2(6,7)
            w[i] = 1.5
        elif par >= reg/20 and par < reg/16: #2(6,7)
            w[i] = 1.38
        else:
            w[i] = 1.5 - 1.5*(par/reg)**(0.8)
            #w[i] = 1.05 - 0.13*(par/(reg/24))**2

    '''
        if par <= reg/64:
            w[i] = 1.1 - 0.05*(par/(reg/64))
        elif par > reg/64 and par <= reg/32:
            w[i] = 1.05 - 0.05*(par/(reg/32))
        elif par > reg/32 and par <= reg/24:
            w[i] = 1.0 - 0.05*(par/(reg/24))
    '''

    if waveform =="2":
        if w[i] * w[i-1] > 0:
            par += 1
        else:
            par = 0
        if w[i] == 1:
            #w[i] = 0.8 + math.log(0.2*(par/reg)+1)
            #test1
            #w[i] = 0.8 + 0.2*(par/reg)**2
            #test2
            #w[i] = 0.8 + 0.2*math.sqrt(par/reg)
            #test3
            #w[i] = 1.0 - 0.2*(par/reg)**2
            #test4
            #w[i] = 1.0 - 0.2*math.sqrt(par/reg)
            #test b1
            #w[i] = 1.0 - 0.5*(par/reg)**2
            #test b2
            #w[i] = 1.0 - 0.5*math.sqrt(par/reg)

            #test c
            #if par <= reg/8:
             #   w[i] = 1.0 - 0.5*(par/(reg/8))**(1/3)
            #else:
             #   w[i] = 0.8 - 0.2*math.sqrt(par/reg)

            #test d
            #if par <= reg/16:
             #   w[i] = 1.5 - 0.5*(par/(reg/8))**(1/3)
            #elif par > reg/16 and par <= reg/8:
             #   w[i] = 0.8
            #else:
             #   w[i] = 0.8 - 0.2*math.sqrt(par/reg)

            #test e
            #if par <= reg/8:
            #    w[i] = 1.4 - 0.6*(par/(reg/8))**(1/3)
            #else:
            #    w[i] = 0.8 - 0.2*math.sqrt((par-reg/8)/(7/8*reg))

            #test f
            #if par <= reg/8:
            #    w[i] = 1.46 - 0.76*(par/(reg/8))**(1/2)
            #else:
            #    w[i] = 0.7 - 0.2*math.sqrt((par-reg/8)/(7/8*reg))

            #test g
            #if par <= reg/8:
            #    w[i] = 1.6 - 0.8*(par/(reg/8))**(1/3)
            #else:
            #    w[i] = 0.8 - 0.1*math.sqrt((par-reg/8)/(7/8*reg))

            #final adjust
            if par < reg/64: #2(0,1)
                w[i] = 1.25
            elif par >= reg/64 and par < reg/32: #2(2,3)
                w[i] = 1.3
            elif par >= reg/32 and par < reg/24: #2(4,5)
                w[i] = 1.275
            elif par >= reg/24 and par < reg/16: #2(6,7)
                w[i] = 1.2
            elif par >= reg/16 and par <= reg/8: #9(8~16)
                #w[i] = 1.0 - 0.2*((par-reg/16)/(reg/16))
                w[i] = 1.0 - 0.2*((par-reg/16)/(reg/16))
            else:
                #w[i] = 0.8 - 0.1*math.sqrt((par-reg/8)/(7/8*reg))
                w[i] = 0.8 - 0.09*math.sqrt((par-reg/8)/(7/8*reg))


        else:
            #w[i] = -0.8 - math.log(0.2*(par/reg)+1)
            #test1
            #w[i] = -0.8 - 0.2*(par/reg)**2    
            #test2
            #w[i] = -0.8 - 0.2*math.sqrt(par/reg)
            #test3
            #w[i] = -1.0 + 0.2*(par/reg)**2
            #test4
            #w[i] = -1.0 + 0.2*math.sqrt(par/reg)
            #test b1
            #w[i] = -1.0 + 0.5*(par/reg)**2
            #test b2
            #w[i] = -1.0 + 0.5*math.sqrt(par/reg)

            #test c
            #if par <= reg/8:
             #   w[i] = -1.0 + 0.5*(par/(reg/8))**(1/3)
            #else:
             #   w[i] = -0.8 + 0.2*math.sqrt(par/reg)

            #test d
            #if par <= reg/16:
            #    w[i] = -1.5 + 0.5*(par/(reg/8))**(1/3)
            #elif par > reg/16 and par <= reg/8:
            #    w[i] = -0.8
            #else:
            #    w[i] = -0.8 + 0.2*math.sqrt(par/reg)
            
            #test e
            #if par <= reg/8:
            #    w[i] = -1.4 + 0.6*(par/(reg/8))**(1/3)
            #else:
            #    w[i] = -0.8 + 0.2*math.sqrt((par-reg/8)/(7/8*reg))

            #test f
            #if par <= reg/8:
            #    w[i] = -1.46 + 0.76*(par/(reg/8))**(1/2)
            #else:
            #    w[i] = -0.7 + 0.2*math.sqrt((par-reg/8)/(7/8*reg))

            #test g
            #if par <= reg/8:
            #    w[i] = -1.6 + 0.8*(par/(reg/8))**(1/3)
            #else:
            #    w[i] = -0.8 + 0.1*math.sqrt((par-reg/8)/(7/8*reg))

            #final adjust
            if par < reg/64: #2(0,1)
                w[i] = -1.25
            elif par >= reg/64 and par < reg/32: #2(2,3)
                w[i] = -1.3
            elif par >= reg/32 and par < reg/24: #2(4,5)
                w[i] = -1.275
            elif par >= reg/24 and par < reg/16: #2(6,7)
                w[i] = -1.2
            elif par >= reg/16 and par <= reg/8: #9(8~16)
                #w[i] = -1.0 + 0.2*((par-reg/16)/(reg/16))
                w[i] = -1.0 + 0.2*((par-reg/16)/(reg/16))
            else:
                #w[i] = -0.8 + 0.1*math.sqrt((par-reg/8)/(7/8*reg))
                w[i] = -0.8 + 0.09*math.sqrt((par-reg/8)/(7/8*reg))

for i in range(int(S)):
    w[i] = int(10000*w[i])

np.savetxt("generated_waveform.txt",w,fmt='%.1d')

#Waveform Graph output
Divider = int(2)
y = [0]*int(S/Divider)
for i in range(0,int(S/Divider)):
    y[i] = int(w[i])
#x = range(0,int(S/Divider))
t= np.arange(start=0,stop=st*int(S/Divider),step=st)
x = t
fig = pyp.figure(figsize=(10,5))
pyp.title("Waveform Graph", {"fontsize":25})
#pyp.xlabel("samples", {"fontsize":15})
pyp.xlabel("time[ns]", {"fontsize":15})
pyp.ylabel("amplitude", {"fontsize":15})
pyp.plot(x,y, label='graph')
pyp.legend()
pyp.show()
fig.savefig('wave.png', bbox_inches='tight', dpi=150)
pyp.clf()
#-//-

#Fouriet Transform Output
N=int(S/Divider)
Y = fft(y, N)
df = Fs/N
Shifted_Y = fftshift(Y)
Shifted_sampleIndex = np.arange(-N//2,N//2)
Shifted_f = Shifted_sampleIndex*df

pyp.stem(Shifted_f, np.abs(Shifted_Y)/N, use_line_collection=True)
pyp.xlabel("frequency[MHz]"), pyp.ylabel("amplitude")
fig.savefig('fourier.png', bbox_inches='tight', dpi=150)
