# coding: utf-8
import serial,time,sys
from random import randint
fecha = "" # Fecha de ejemplo en formato DDMMAA (Solo fechas validas!)
espera = 0
loop = 0
arduino = serial.Serial('COM3', 9600, timeout=.1) # debe coincidir con los baudios y el puerto arduino

while True:
    if espera==0:
        print "Enviando fecha en puerto COM", (loop+1)
        fecha = str(randint(1,31)).zfill(2)+str(randint(1,12)).zfill(2)+str(randint(0,99)).zfill(2)
        
        """# Testear tiempos variables de espera
        e = randint(1,5)
        t = 'CORTO'
        if (e==5 and loop>0):
            e = randint(30,60)
            t = 'LARGO'
        for i in xrange(e):
            sys.stdout.write("Esperando un tiempo %s de %d segundos     \r" % (t,e-i))
            sys.stdout.flush()
            time.sleep(1) # Espera un tiempo variable corto (como usarios interactuando)
        #"""

        arduino.write(fecha) # Envia fecha de ejemplo a serial para python
        time.sleep(0.1)
        espera=1 # espera antes de enviar una nueva fecha
        loop+=1
        print "Eperando respuesta por puerto COM...                "

    else:
        msg = arduino.readline() #capturamos la respuesta y eliminamos el salto de linea final
        if msg:
            print "Respuesta recibida en puerto COM"
            print ">>",msg
            time.sleep(0.1)
            espera=0 # si recibe cualquier respuesta en serial deja de esperar
