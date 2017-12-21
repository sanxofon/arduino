# coding: utf-8
# Author Santiago Chávez Novaro
# Calculadora p/q de operaciones matemáticas (y musiquita!)
from __future__ import division

import os,sys
import serial
from Tkinter import Tk, Label, Canvas, StringVar
from numericStringParser import *
import time
import winsound
import logging
import datetime

import musica as mu

# Log de uso
fecha = datetime.datetime.now()
logfile = fecha.strftime("%y%m")+".log"
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='log/'+logfile, level=logging.INFO)
logging.info("INFO\tInicio de programa")
def current_iso8601():
    return time.strftime("%Y%m%dT%H%M%SZ", time.localtime())

"""
    CONTROLES ASIGNADOS:
         ______________________________________________
        |                                              |
        |  TECLAS ACEPTADAS:                           |
        |     0-9  => Numeros                          |
        |       e  => Euler                            |
        |       h  => Pi (π)                           |
        |       f  => Phi (φ)                          |
        |       t  => Multiplicar (×)                  |
        |       m  => Sumar                            |
        |       n  => Restar                           |
        |       r  => Raiz cuadrada (√)                |
        |       p  => Establecer dividendo             |
        |       q  => Establecer divisor (dividir)     |
        |       i  => Igual a                          |
        |       x  => Backspace                        |
        |       c  => Reiniciar                        |
        |       -----------------------                |
        |       a  => Avanzar (enviar a Arduino)       |
        |       s  => Stop (pausar envio a Arduino)    |
        |       -----------------------                |
        |       k  => Salir del programa (oculto)      |
        |______________________________________________|
 
    INSTRUCCIONES:
        
        1. Definir VARIABLES GENERALES de Desarrollo o Producción en código (VER __init__ ABAJO)
            1.1. Definir puerto, baudios del puerto serial
            1.2. Definir presición máxima para operaciones y constantes
            1.3. Definir "debug", "sendToDisplay", "timeout", "fullscreen" y "utrawidescreen"

        2. Ejecutar el programa con el acceso directo que se encuentra en la misma carpeta.
            2.1. Ejecutar desde consola para debug en carpeta:
                [WidowsKey]+R
                "cmd" + [ENTER]
                $ cd c:\Users\user\Ruta_ALaCarpeta\
                $ python calculadora.py
        
        3. Iniciado el programa, escribir operación en dividendo (p) y/o divisor (q)
            3.1. El paréntesis de la raiz se cierra clicando "r" por segunda vez.
            3.2. Apretar [ENTER] para mostrar el resultado (en debug) o comenzar envío a Display
        
        4. Apretar "acelerar" (a) y "desacelerar" (s) y el envío de caracteres por el serial
            4.1. En el envío de números (uno por uno a arduino) se cambia el número que 
            tenga el punto decimal a la derecha, por la letra mayúscula que corresponda:
                A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=0
    
    EJEMPLOS:
        1/7 = 0.142857, periodo de 6 dígitos
        1/17 = 0.0588235294117647, periodo de 16 dígitos
        1/19 = 0.052631578947368421, periodo de 18 dígitos
        1/23 = 0.0434782608695652173913, periodo de 22 dígitos
        1/29 = 0.0344827586206896551724137931, periodo de 28 dígitos
        1/47 = 0.0212765957446808510638297872340425531914893617, periodo de 46 dígitos
        1/59 = 0.0169491525423728813559322033898305084745762711864406779661, periodo de 58 dígitos
        1/61 = 0.016393442622950819672131147540983606557377049180327868852459, periodo de 60 dígitos
        1/97 = 0.010309278350515463917525773195876288659793814432989690721649484536082474226804123711340206185567, periodo de 96 dígitos

    MUSICALES:
        BatMan - 66443344/99999999

    BUGS:
        - DEBUG ARDUINO: Caso NÚMERO NEGATIVO EN RESULTADO, se envía guión al inicio: -3.141592...
                            Debe existir signo de menos en arduino !!!
        - DEBUG ARDUINO: Caso RESET, el resultado debe vaciarse en display. 
                            Falta definir caracter de RESET !!!

"""
class calculadora(object):
    def __init__(self):

        # DEFINIR VARIABLES GENERALES
        self.maxprec = 20000        # Precision numérica de la calculadora - Dev:1000, Prd: 20000
        self.debuguear = 1          # Debug. Muestra en pantalla lo que se envia al display
        self.sendToDisplay = 0      # Enviar dígitos a Display (on/off)
        self.ard_comm = 'COM3'      # Serial com port, debe coincidir con los baudios y el puerto arduino
        self.ard_baud = 9600        # Serial baud rate, debe coincidir con los baudios y el puerto arduino
        self.ard_tiot = 0.1         # Serial timeout 100ms, testeado con arduino UNO
        self.fullscreen = 0         # Abrir en pantalla completa. Dev: 0, Prd: 1
        self.ultrawidescreen = 0    # Monitor UltraWideScreen

    def iniciar(self, master):
        ######### VARIABLES GENERALES #########
        # Velocidad (lista de velocidades en milisegundos)
        self.velist = [1000,700,500,400,300,200,150,100]
        self.velmax = len(self.velist)-1
        self.vel = -1
        self.memvel = 0

        # Debug
        self.porcionlen = 70 # Porcion a mostrar
        self.porcion = ''
        self.playsounds = 0 # VERSION DE PRUEBA!!
        self.playwaves = 1 # VERSION DE PRUEBA!!

        #Arduino COMM (Display)
        if self.sendToDisplay>0:
            # debe coincidir con los baudios y el puerto arduino
            self.arduino = serial.Serial(self.ard_comm, self.ard_baud, timeout=self.ard_tiot)
            time.sleep(1)
            if self.sendToDisplay>0:
                self.arduino.write('N') # RESET DYSPLAY
                time.sleep(1)

        # nsp class
        self.nsp = NumericStringParser()
        self.nsp.setPresicion(self.maxprec) #Set presicion

        # Contador de envio a Arduino
        self.resultadoAduino = ''
        self.resultadoNormal = ''
        self.contador = -1
        self._job = None

        #######################################
        if self.playwaves>0:
            p = mu.pyaudio.PyAudio()

            self.stream = p.open(format=mu.pyaudio.paFloat32,
                            channels=mu.CHANNELS,
                            rate=mu.RATE,
                            output=True,
                            stream_callback=mu.callback)

            self.stream.stop_stream()
        #######################################


        self.master = master
        if self.fullscreen>0:
            # Full screen
            master.overrideredirect(True)
            master.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
            master.focus_set()  # <-- move focus to this widget
            # Otra opción
            # master.attributes('-fullscreen', True)
        else:
            master.geometry("%dx%d+0+0" % (master.winfo_screenwidth()-16, master.winfo_screenheight()-80))

        master.title("Calculadora")

        master.bind("<Escape>", lambda e: e.widget.quit()) # Python 2
        master.bind("<Key>", self.recibeChar)

        self.dondestoy = 'p'

        # Dividendo p
        self.dividendostr = ""
        self.dividendo = StringVar()
        self.dividendo.set(self.dividendostr)
        if self.ultrawidescreen>0:
            # UltraWide Screen
            self.labelp = Label(master, textvariable=self.dividendo, bg="#fd0", width=18, justify="center", font=("Roboto", 192))
        else:
            # 16:9 Screen
            self.labelp = Label(master, textvariable=self.dividendo, bg="#fd0", width=21, justify="center", font=("Roboto", 96))

        self.line = Canvas(master, width=master.winfo_screenwidth(), height=50)
        # self.line.create_rectangle(0, 0, master.winfo_screenwidth(), 20, outline="#000", fill="#000")
        self.line.create_line(0, 0, master.winfo_screenwidth(), 0, fill="#000",width=50)

        # Divisor q
        self.divisorstr = "1"
        self.divisor = StringVar()
        self.divisor.set(self.divisorstr)
        if self.ultrawidescreen>0:
            # UltraWide Screen
            self.labelq = Label(master, textvariable=self.divisor, bg="#eee", fg="#aaa", width=18, justify="center", font=("Roboto", 192))
        else:
            # 16:9 Screen
            self.labelq = Label(master, textvariable=self.divisor, bg="#eee", fg="#aaa", width=21, justify="center", font=("Roboto", 96))

        # Resultado res
        self.resultastr = ""
        self.resulta = StringVar()
        self.resulta.set(self.resultastr)
        if self.ultrawidescreen>0:
            # UltraWide Screen
            self.labelr = Label(master, textvariable=self.resulta, bg="#eee", width=213, justify="left", font=("Roboto", 16))
        else:
            # 16:9 Screen
            self.labelr = Label(master, textvariable=self.resulta, bg="#eee", width=120, justify="left", font=("Roboto", 16))

        # Posiciona
        self.line.place(relx=0, rely=.495)
        self.labelp.place(relx=0, rely=.22)
        self.labelq.place(relx=0, rely=.545)
        self.labelr.place(relx=0, rely=.80)

        # init timer de envio a arduino
        # self.onUpdate()

        #######################################
    def filtrar(self,s):
        if '.' in s:
            r = {
                '1':'A',
                '2': 'B',
                '3': 'C',
                '4': 'D',
                '5': 'E',
                '6': 'F',
                '7': 'G',
                '8': 'H',
                '9': 'I',
                '0': 'J'
            }
            s = s.split('.')
            c = s[0][-1:]
            s[0] = s[0][0:-1]
            return s[0]+r[c]+s[1]
        else:
            return s

    def modcad(self,cad,c):
        cad = cad.decode('utf-8')
        p = cad[-1:]
        if isinstance(c, int):
            if (len(cad)>=c):
                cad = cad[:-c]
        else:
            c = c.decode('utf-8')
            cad = cad+c
        cad = cad.encode('utf-8')
        return cad

    def recibeChar(self,event):
        k = event.keycode
        c = event.char
        p = str(self.dividendostr)
        q = str(self.divisorstr)

        # # Test input del teclado
        # self.resultastr = c+': ',str(k)+': '+str(event.state)
        # self.resulta.set(self.resultastr)
        # return
        
        if self.debuguear==0:
            self.resultastr = ''
            self.resulta.set(self.resultastr)

        numrs = ['0','1','2','3','4','5','6','7','8','9']
        if (self.dondestoy=='q'):
            cadena = q
            # if cadena=='1':
            #     cadena = ''
        else:
            cadena = p
        # SALIDAS
        if c=='c': # c
            # reiniciar programa
            self.calculadora('REINICIAR', '', p, q)
            return
            # return '','REINICIAR'
        elif c=='k': # k
            # salir del programa
            self.calculadora('SALIR', '', p, q)
            return
            # return '','SALIR'

        # AVANZAR Y STOP
        if c=='a': # Avanza/Acelera
            if self.vel<0 and self.resultadoAduino!='':
                self.vel=0
                self.calcelUpdate('Avanzar')
                self.onUpdate()
            elif self.vel<self.velmax:
                self.vel = self.vel+1
            return
            # return '','REINICIAR'
        elif c=='s': # Stop
            if self.vel>=0:
                self.vel = self.vel-1
            return

        # IGUAL A
        elif k==10 or k==13 or c=='i':# or k==61: # [ENTER] o [=] > Salto de línea o igual: '\n' ó '\r' ó '='
            # imprimir cadena RESULTADO
            self.calculadora('RESULTADO', cadena, p, q)
            return
            # return cadena,'RESULTADO'

        # ESCRITURA NORMAL
        elif k == 8 or c=='x': # BACKSPACE
            # recortar cadena un digito
            cadena = self.modcad(cadena,1)
        elif c in numrs: # NUMEROS 0-9
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        # elif c==',' or c=='.': # COMA o PUNTO
        #     c='.' # Siempre usa punto
        #     # incrementa la cadena con c
        #     cadena = self.modcad(cadena,str(c))

        # NUMEROS ESPECIALES e y pi
        elif c=='e':    # e => 101
            # Euler's number => 'e'
            c = 'e'
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        elif c=='h':    # h => 104
            # PI => 'h'
            c = 'π'
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        elif c=='f':    # f => 104
            # PI => 'h'
            c = 'φ'
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        
        # OPERACIONES SIMPLES: * + - /
        elif c=='*': # * => 42
            # Multiplicación => Reemplaza asterisco con signo de multiplicacion ×
            c = '×'
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        elif c=='+' or c=='m':    # + => 43
            # incrementa la cadena con c
            c = '+'
            cadena = self.modcad(cadena,str(c))
        elif c=='-' or c=='n':    # - => 45
            # incrementa la cadena con c
            c = '-'
            cadena = self.modcad(cadena,str(c))
        elif c=='r':    # r
            # SQRT => 'r'
            rcadena = cadena[::-1]
            if '(' in rcadena:
                if ')' in rcadena:
                    ax = rcadena.index('(')
                    cx = rcadena.index(')')
                    if ax<cx:
                        c=')'
                    else:
                        c = '√('
                else:
                    c=')'
            else:
                c = '√('
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        elif c=='p':    # p
            # Debe enviar al valor p sólo si no estamos ahí
            if (self.dondestoy!='p'):
                self.calculadora('SETP', cadena, p, q)
                return
        elif c=='q':    # q
            # Debe enviar al valor q sólo si no estamos ahí
            if (self.dondestoy!='q'):
                self.calculadora('SETQ', cadena, p, q)
                return

        if (self.dondestoy=='p'):
            p = cadena
        if (self.dondestoy=='q'):
            q = cadena
        # if (q==''):
        #     q = '1'
        self.operacion(p,q)

    def calculadora(self, estado, cadena='', p='', q=''):
        if (estado=='RESULTADO'):
            self.calcelUpdate('Nuevo resultado')
            self.porcion = ''
            self.memvel = 0 #Memoria de la volicidad actual
            if self.vel>0:
                self.memvel = self.vel
            self.vel = -1 # Stop timer
            self.contador = -1 # Reset timer
            if self.sendToDisplay>0:
                self.arduino.write('N') # RESET DYSPLAY
                time.sleep(1)
            if (self.dondestoy=='p'):
                p = cadena
            if (self.dondestoy=='q'):
                q = cadena
            if p=='':
                p='0'
            if (q==''):
                q='1'
            rcadena = p[::-1]
            if '(' in rcadena:
                if ')' in rcadena:
                    ax = rcadena.index('(')
                    cx = rcadena.index(')')
                    if ax<cx:
                        p=p+')'
                else:
                    p=p+')'
            rcadena = q[::-1]
            if '(' in rcadena:
                if ')' in rcadena:
                    ax = rcadena.index('(')
                    cx = rcadena.index(')')
                    if ax<cx:
                        q=q+')'
                else:
                    q=q+')'
            self.resultado(p,q)

        if (estado=='REINICIAR'):
            self.calcelUpdate('Reiniciar')
            self.resultadoNormal = ''
            self.resultadoAduino = ''
            self.vel = -1 # Stop timer
            self.contador = -1 # Reset timer
            self.operacion(p='',q=1)
            self.resultastr = ''
            self.resulta.set(self.resultastr)
            self.dondestoy = 'p'
            self.labelp.config(bg="#fd0")
            self.labelq.config(bg="#eee")
            if self.sendToDisplay>0:
                self.arduino.write('N') # RESET DYSPLAY
                time.sleep(1)
            # self.calculadora()
        if (estado=='SALIR'):
            self.calcelUpdate()
            logging.info("INFO\tSalir del programa")
            time.sleep(1)
            self.vel = -1 # Stop timer
            self.master.quit()
            # return
        if (estado=='SETP'):
            q = cadena
            if '(' in q and ')' not in q:
                q=q+')'
            if q=='0' or q=='':
                self.divisorstr = str('1')
                self.divisor.set(self.divisorstr)
                self.labelq.config(fg="#aaa")
            self.dondestoy = 'p'
            self.labelp.config(bg="#fd0")
            self.labelq.config(bg="#eee")
            # self.calculadora(p,p,q,dondestoy)
        if (estado=='SETQ'):
            p = cadena
            if '(' in p and ')' not in p:
                p=p+')'
            if q=='1':
                self.divisorstr = str('')
                self.divisor.set(self.divisorstr)
                self.labelq.config(fg="#aaa")
            self.dondestoy = 'q'
            self.labelp.config(bg="#eee")
            self.labelq.config(bg="#fd0")
            # self.calculadora(q,p,q,dondestoy)

    def maxlen(self, p,q):
        maxlen = len(str(p))
        if (len(str(q))>maxlen):
            maxlen = len(str(q))
        lp = len(str(p))
        lq = len(str(q))
        return maxlen,lp,lq

    def operacion(self, p='',q=1):
        ml,lp,lq = self.maxlen(p,q)
        self.dividendostr = str(p)
        self.dividendo.set(self.dividendostr)
        self.divisorstr = str(q)
        self.divisor.set(self.divisorstr)

        # Color gris en divisor cuando es 1
        if self.divisorstr != "1":
            self.labelq.config(fg="#000")
        else:
            self.labelq.config(fg="#aaa")

    def resultado(self, p,q):
        self.calcelUpdate()
        ml,lp,lq = self.maxlen(p,q)
        self.dividendostr = str(p)
        self.dividendo.set(self.dividendostr)
        self.divisorstr = str(q)
        self.divisor.set(self.divisorstr)

        # Color gris en divisor cuando es 1
        if self.divisorstr != "1":
            self.labelq.config(fg="#000")
        else:
            self.labelq.config(fg="#aaa")

        ################################################
        # Calcula p/q en la presición definida
        equa = '('+p+')/('+q+')'
        res = self.nsp.eval(equa)

        # RESULTADO COMO CADENA
        nres = ''
        sres = str(res)
        if sres == 'ERROR':
            self.resultastr = sres
            self.resulta.set(self.resultastr)
            logging.info("ERROR\t"+equa)
            return
        # Set start envio Arduino
        self.resultadoNormal = sres
        self.resultadoAduino = self.filtrar(sres)
        self.contador = -1
        self.vel = self.memvel
        logging.info("OK\t"+equa)
        # Inicia envío a display arduino
        self.onUpdate()

    def calcelUpdate(self,quien=''):
        if self.playwaves>0:
            mu.newfreq = 0
        if self._job is not None:
            if quien!='':
                logging.info("CANCEL\t"+quien)
            self.master.after_cancel(self._job)
            self._job = None

    def onUpdate(self):
        self.calcelUpdate()
        # Actualiza el caracter enviado, la posición y el estado actual (pausa/play)
        self.contador = self.contador+1
        inicio = self.contador-self.porcionlen
        if self.contador>self.maxprec:
            self.porcion = ''
            self.contador = 0
            self.resultado(self.dividendostr, self.divisorstr)
            if self.playwaves>0:
                mu.newfreq = 0
            return
        if inicio<0:
            inicio=0
        if self.contador>len(self.resultadoAduino)-1:
            enviar = '0'
        else:
            enviar = self.resultadoAduino[self.contador]
        self.porcion = self.porcion+enviar
        if len(self.porcion)>self.porcionlen-1:
            self.porcion = self.porcion[-self.porcionlen:]

        if self.debuguear>0:
            salida = u"Resultado: "+self.resultadoNormal[0:self.porcionlen]
            salida = salida+u"\nVelocidad: "+str(self.velist[self.vel])+" ms"
            tiempofaltante = round(self.velist[self.vel]*(len(self.resultadoAduino)-self.contador)/1000)
            m, s = divmod(tiempofaltante, 60)
            h, m = divmod(m, 60)
            salida = salida+u"\nTiempo restante: "+str("%d:%02d:%02d" % (h, m, s))+" hms"
            salida = salida+u"\nPosición: "+str(self.contador)+" / "+str(len(self.resultadoAduino))
            salida = salida+u"\nDígito: "+enviar
            salida = salida+u"\nPorción: "+self.porcion.rjust(self.porcionlen, ' ').replace(' ','  ')
            self.resultastr = salida
            self.resulta.set(self.resultastr)
        
        if self.playwaves>0:
            self.stream.start_stream()
            try:
                nx = int(enviar)
            except ValueError:
                nx = -1
                pass
            if nx>0:
                nx = nx-1
            elif nx==0:
                nx=-1
            if nx<0:
                mu.newfreq = 0
            else:
                mu.newfreq = mu.listaFreq[nx]
        
        

        # ENVIO A DISPLAY
        if self.sendToDisplay>0:
            self.arduino.write(enviar) # Envia digito actual a DISPLAY, la pausa la genera el unUpdate mismo
        # DEBUG EN CONSOLA
        if self.debuguear>1:
            print(current_iso8601(),self.contador,self.vel,self.velist[self.vel],enviar)
        # schedule timer para ayutollamarse cada segundo
        if self.vel>=0:
            self._job = self.master.after(self.velist[self.vel], self.onUpdate)

        # Versión de prueba !!!
        if self.playsounds>0 and self.char2wav(enviar)!='':
            corto = ''
            if self.velist[self.vel]<300:
                corto = '_'             
            winsound.PlaySound('wav/'+self.char2wav(enviar)+corto+'.wav',winsound.SND_FILENAME | winsound.SND_ASYNC)

    def char2wav(self,c):
        r = { 'A':'1', 'B':'2', 'C':'3', 'D':'4', 'E':'5', 'G':'7', 'H':'8', 'I':'9', 'J':'0', '-':'0' }
        if c in r.keys():
            c = r[c]
        n = {
            # '1':'c1', '2':'d1', '3':'e1', '4':'f1', '5':'', '6':'g1', '7':'a1', '8':'b1', '9':'c2', '0':'' # Mayor, Silencios: 0, 5
            '1':'c1', '2':'d1', '3':'d1s','4':'e1', '5':'f1','6':'g1','7':'a1', '8':'b1', '9':'c2', '0':'' # Mayor/Menor, Silencio: 0
        }
        return n[c]

root = Tk()
calc = calculadora();
calc.iniciar(root);
root.mainloop()