import numpy as np
import math
from matplotlib import pyplot as pyp
from scipy.fftpack import fft, fftshift, fftfreq
from scipy.signal import find_peaks
#Sampling Frequency (245.76*N/M) [MHz]
Fs = 3932.160
#Fs = 6512.64

#Target Frequency[MHz]
print("Output Frequency in [MHz]: ")
Ft = int(input())

#Center Frequency generated
Fg = 0

#Generated samples
S = 0

#samples time distance
st = 1000/Fs

#waveform(0:sin,1:sawtooth,2:square,else:triangle)
print("Waveform(0:sine, 1:sawtooth, 2: square, 3:triangle): ")
waveform = input()

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

#waveform data
w = np.zeros(S)

for i in range(int(S)):
    if waveform == "0":
        #sine
        w[i] = math.sin(2*math.pi*i*(Fg/Fs))
    elif waveform =="1":
        #sawtooth
        w[i] = ((Fs/Fg)-i%(Fs/Fg))/(Fs/Fg)*2 -1
    elif waveform =="2":
        #square
        if math.sin(2*math.pi*i*(Fg/Fs))>=0: w[i] = 1
        else: w[i] = -1
    else:
        #triangle
        w[i] = ((Fs/(2*Fg))-abs((Fs/(2*Fg))-i%(Fs/Fg)))/(Fs/(2*Fg))

for i in range(int(S)):
    w[i] = int(32767*w[i])/2

np.savetxt("generated_waveform.txt",w,fmt='%.1d')

#Waveform Graph output
Divider = int(100)
y = [0]*int(S/Divider)
for i in range(0,int(S/Divider)):
    y[i] = int(w[i])
#x = range(0,int(S/Divider))
t= np.arange(start=0,stop=st*int(S/Divider),step=st)
x = t
fig = pyp.figure(figsize=(10,5))
pyp.title("Waveform Graph", {"fontsize":25})
pyp.xlabel("time[ns]", {"fontsize":15})
pyp.ylabel("amplitude", {"fontsize":15})
pyp.plot(x,y, label='graph')
pyp.legend()
pyp.show()
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
