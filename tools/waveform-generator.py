import numpy as np
import math
from matplotlib import pyplot as pyp
from scipy.fftpack import fft, fftshift

#Sampling Frequency[MHz]
Fs = 3932.160

#Target Frequency[MHz]
print("Target Frequency in [MHz]: ")
Ft = int(input())

#Generated Frequency[MHz]
Fg = 0

#Generated Samples
S = 0

#Samples time distance[ns]
st = 1000/Fs

#Deciding the samples for Fg
for samples in range(1024,32768,32):
    #Base Frequency
    Fb = Fs/samples
    F1 = int(Ft/Fb)*Fb
    F2 = (int(Ft/Fb)+1)*Fb
    if abs(F1-Ft) < abs(F2-Ft):
        if abs(F1-Ft) < abs(Fg-Ft):
            Fg = F1
            S = samples
    else:
        if abs(F2-Ft) < abs(Fg-Ft):
            Fg = F2
            S = samples

#Waveform data
w = np.zeros(S)

#sinewave
for i in range(int(S)):
    w[i] = int(math.sin(2*math.pi*i*(Fg/Fs))*32767)

np.savetxt("generated_waveform.txt",w,fmt='%.1d')

#Waveform Graph output
Divider = int(100)
y = [0]*int(S/Divider)
for i in range(0,int(S/Divider)):
    y[i] = int(w[i])
x= np.arange(start=0,stop=st*int(S/Divider),step=st)
fig = pyp.figure(figsize=(10,5))
pyp.title("Waveform Graph", {"fontsize":25})
pyp.xlabel("time[ns]", {"fontsize":15})
pyp.ylabel("amplitude[LSB]", {"fontsize":15})
pyp.plot(x,y,label="wave")
pyp.legend()
#pyp.show()
fig.savefig('wave.png', bbox_inches='tight', dpi=150)
pyp.clf()

#Fouriet Transform Output
N=int(S/Divider)
Y = fft(y, N)
df = Fs/N
Shifted_Y = fftshift(Y)
Shifted_sampleIndex = np.arange(-N//2,N//2)
Shifted_f = Shifted_sampleIndex*df
pyp.stem(Shifted_f, np.abs(Shifted_Y)/N, use_line_collection=True)
pyp.xlabel("frequency[MHz]"), pyp.ylabel("amplitude[LSB]")
fig.savefig('fourier.png', bbox_inches='tight', dpi=150)
