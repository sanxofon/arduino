#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyaudio
import numpy as np
import time
import sys
# import keyboard

# Iniciar sonando
streamOn = 0

# Globales
CHANNELS = 2
RATE = 44100
TT = time.time()
freq = 100.0
newfreq = 100.0
phase = 0

escal = 12.0 # Subdivisiones en una octava
iniscal = -1 # Octava más baja a partir de A central
troot = np.power(2.0,1.0/escal); # escal'ava raiz de 2
acentral = 434.0 # A central en Hz
# Lista de intervalos
listerval = [0, 2, 3, 4, 5, 7, 9, 11, 12]
listaFreq = []
newfreq = 0

# FUNCIONES ---------------------------------------------------------------------------
#continuo o afinado
def setLF():
    global listaFreq,listerval,escal,iniscal
    listaFreq = []
    for i in listerval:
        listaFreq.append(calcStepFreqJ(i+(int(escal)*iniscal)))

def callback(in_data, frame_count, time_info, status):
    global TT,phase,freq,newfreq
    if newfreq != freq:
        phase = 2*np.pi*TT*(freq-newfreq)+phase
        freq=newfreq
    left = (np.sin(phase+2*np.pi*freq*(TT+np.arange(frame_count)/float(RATE))))
    data = np.zeros((left.shape[0]*2,),np.float32)
    data[::2] = left
    data[1::2] = left
    TT+=frame_count/float(RATE)
    return (data, pyaudio.paContinue)

# Recibe la frecuencia en Hertz
# Regresa el numero de pasos desde A central
def calcFreqStep(f): 
    global troot,acentral
    d = 1000000.0 # six zeros before decimal point
    return np.round(d*(np.log(f/acentral)/np.log(troot)))/d;

# Recibe el numero de pasos (semitonos) desde A central (440)
# Regresa la frecuencia en Hertz
def calcStepFreq(s):
    global troot,acentral
    return acentral * np.power(troot,s)

# Recibe el numero de pasos (semitonos justos)
# Regresa la frecuencia en Hertz
def calcStepFreqJ(s):
    global acentral,escal,iniscal
    mo = (s % 12)
    di = np.floor(s / escal)
    if mo<0:
        mo = mo+12
    # Lista de racionales justos
    t = [
        1.0,        #Tonica
        25.0/24.0,  # Segunda menor
        9.0/8.0,    # Segunda mayor
        6.0/5.0,    # Tercera menor
        5.0/4.0,    # Tercera mayor
        4.0/3.0,    # Cuarta
        45.0/32.0,  # Quinta dim
        3.0/2.0,    # Quinta
        8.0/5.0,    # Sexta menor
        5.0/3.0,    # Sexta mayor
        9.0/5.0,    # Septima menor
        15.0/8.0,   #  Septima mayor
    ]
    return (acentral * t[mo]*np.power(2,di))

# FUNCIONES ---------------------------------------------------------------------------
setLF()

# print(listaFreq)
"""
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paFloat32,
                channels=CHANNELS,
                rate=RATE,
                output=True,
                stream_callback=callback)

if streamOn>0:
    stream.start_stream()
else:
    stream.stop_stream()


try:
    while 1:
        if keyboard.is_pressed('esc'):#if space is pressed
            stream.stop_stream()
            stream.close()
            p.terminate()
            break
        elif keyboard.is_pressed('space'):#if space is pressed
            if streamOn>0: 
                streamOn = 0 
                stream.stop_stream()
            else:
                streamOn = 1 
                stream.start_stream()
        else:
            i=-1
            if keyboard.is_pressed('1'):
                i=0
            elif keyboard.is_pressed('2'):
                i=1
            elif keyboard.is_pressed('3'):
                i=2
            elif keyboard.is_pressed('4'):
                i=3
            elif keyboard.is_pressed('5'):
                i=4
            elif keyboard.is_pressed('6'):
                i=5
            elif keyboard.is_pressed('7'):
                i=6
            elif keyboard.is_pressed('8'):
                i=7
            elif keyboard.is_pressed('9'):
                i=8
            elif keyboard.is_pressed('0'):
                newfreq = 0
                # streamOn = 0 
                # stream.stop_stream()
            if i>=0:
                if streamOn<1:
                    streamOn = 1 
                    stream.start_stream()
                newfreq = listaFreq[i]
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
#"""