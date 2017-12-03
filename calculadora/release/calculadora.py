# coding: utf-8
# Santiago Chávez Novaro
from __future__ import division
# from __future__ import print_function

# from decimal import *
# import readchar
import os,sys
import serial
from Tkinter import Tk, Label, Canvas, StringVar
from numericStringParser import *
# from primefac import *
# import re
import time

def current_iso8601():
    """Get current date and time in ISO8601"""
    # https://en.wikipedia.org/wiki/ISO_8601
    # https://xkcd.com/1179/
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

"""____________________________________________
|                                              |
|  TECLAS ACEPTADAS:                           |
|     0-9  => Numeros                          |
|       e  => Euler                            |
|       h  => Pi (π)                           |
|       f  => Phi (φ)                          |
|       *  => Multiplicar (×)                  |
|       +  => Sumar                            |
|       -  => Restar                           |
|       r  => Raiz cuadrada (√)                |
|       p  => Establecer dividendo             |
|       q  => Establecer divisor (dividir)     |
|  [ENTER] => Igual a                          |
|        c => Reiniciar                        |
|        -----------------------               |
|        a => Avanzar (enviar a Arduino)       |
|        s => Stop (pausar envio a Arduino)    |
|        -----------------------               |
|        k => Salir del programa (oculto)      |
|____________________________________________"""

"""
    ToDo:
        ✓ Alcarar el 1 del divisor cuando aún no se ha seteado
        ✓ Modificar el signo de * por el de × (U+00D7 => c3 97  MULTIPLICATION SIGN) en la vista (similar a PI=>π)
        ✓ Definir presición mínima para operaciones y constantes
        ✓ Implementar "avanzar" (a) y "stop" (s) y el envío de caracteres por el serial uno por uno con timer
        ✓ En el envío de números (uno por uno a arduino) debe de cambiarse el número que 
            tenga el punto decimal a la derecha, por la letra mayúscula que corresponda:
            A=1, B=2, C=3, D=4, E=5, F=6, G=7, H=8, I=9, J=0
        ✓ Generar 0's infinitos para números enteros
        - DEBUG ARDUINO: Caso número negativo en resultado debe existir signo de menos en arduino !!!
"""
class calculadora(object):
    def __init__(self, master):

        ######### VARIABLES ADMIN #############

        # SCREEN
        fullscreen = 1
        ultrawidescreen = 1

        # Velocidad (lista de velocidades en milisegundos)
        self.velist = [1000,700,500,400,300,200,150,100,80,60,40,20,10]

        # Debug
        self.debuguear = 0
        self.porcionlen = 70 # Porcion a mostrar
        self.porcion = ''
        
        # Display out to Arduino (on/off)
        self.sendToDisplay = 1

        #Arduino COMM (Display)
        if self.sendToDisplay>0:
            arduino = serial.Serial('COM3', 9600, timeout=.1) # debe coincidir con los baudios y el puerto arduino
            time.sleep(0.1)

        #######################################
        ######### VARIABLES GENERALES #########

        # nsp class
        self.nsp = NumericStringParser()

        # Vel sets
        self.velmax = len(self.velist)-1
        self.vel = -1

        # Contador de envio a Arduino
        self.resultadoAduino = ''
        self.resultadoNormal = ''
        self.contador = -1
        self._job = None

        #######################################

        self.master = master
        if fullscreen>0:
            # Full screen
            master.overrideredirect(True)
            master.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
            master.focus_set()  # <-- move focus to this widget
            # Otra opción
            # master.attributes('-fullscreen', True)
        else:
            # master.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth()-16, root.winfo_screenheight()-80))
            master.geometry("%dx%d+0+0" % (master.winfo_screenwidth()-16, master.winfo_screenheight()-80))

        master.title("Calculadora")

        master.bind("<Escape>", lambda e: e.widget.quit()) # Python 2
        master.bind("<Key>", self.recibeChar)

        self.dondestoy = 'p'

        # Dividendo p
        self.dividendostr = ""
        self.dividendo = StringVar()
        self.dividendo.set(self.dividendostr)
        if ultrawidescreen>0:
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
        if ultrawidescreen>0:
            # UltraWide Screen
            self.labelq = Label(master, textvariable=self.divisor, bg="#eee", fg="#aaa", width=18, justify="center", font=("Roboto", 192))
        else:
            # 16:9 Screen
            self.labelq = Label(master, textvariable=self.divisor, bg="#eee", fg="#aaa", width=21, justify="center", font=("Roboto", 96))

        # Resultado res
        self.resultastr = ""
        self.resulta = StringVar()
        self.resulta.set(self.resultastr)
        if ultrawidescreen>0:
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
            # if p==')':
            #     if (len(cad)>=c+1):
            #         cad = cad[:-(c+1)]+')'
            # else:
            if (len(cad)>=c):
                cad = cad[:-c]
        else:
            c = c.decode('utf-8')
            # if p==')':
            #     cad = cad[:-1]+c+')'
            # else:
            cad = cad+c
        cad = cad.encode('utf-8')
        return cad

    def recibeChar(self,event):
        # Color gris en divisor cuando es 1
        k = event.keycode
        c = event.char
        p = str(self.dividendostr)
        q = str(self.divisorstr)
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
                self.calcelUpdate()
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
        elif k==10 or k==13 or c=='=':# or k==61: # [ENTER] o [=] > Salto de línea o igual: '\n' ó '\r' ó '='
            # imprimir cadena RESULTADO
            self.calculadora('RESULTADO', cadena, p, q)
            return
            # return cadena,'RESULTADO'

        # ESCRITURA NORMAL
        elif k == 8: # BACKSPACE
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
        elif c=='+':    # + => 43
            # incrementa la cadena con c
            cadena = self.modcad(cadena,str(c))
        elif c=='-':    # - => 45
            # incrementa la cadena con c
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
        elif c=='p':    # p => 112
            # Debe enviar al valor p sólo si no estamos ahí
            if (self.dondestoy!='p'):
                self.calculadora('SETP', cadena, p, q)
                return
                # return cadena, 'SETP'
        elif c=='q':    # q => 113
            # Debe enviar al valor q sólo si no estamos ahí
            if (self.dondestoy!='q'):
                self.calculadora('SETQ', cadena, p, q)
                return
                # return cadena, 'SETQ'

        if (self.dondestoy=='p'):
            p = cadena
        if (self.dondestoy=='q'):
            q = cadena
        # if (q==''):
        #     q = '1'
        self.operacion(p,q)

    def calculadora(self, estado, cadena='', p='', q=''):
        if (estado=='RESULTADO'):
            self.calcelUpdate()
            self.porcion = ''
            self.vel = -1 # Stop timer
            self.contador = -1 # Reset timer
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
            self.calcelUpdate()
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
            # self.calculadora()
        if (estado=='SALIR'):
            self.calcelUpdate()
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
        # Calcula p y q numericamente a floats
        res = self.nsp.eval('('+p+')/('+q+')')

        # RESULTADO COMO CADENA
        nres = ''
        sres = str(res)
        if sres == 'ERROR':
            self.resultastr = sres
            self.resulta.set(self.resultastr)
            return
        # Set start envio Arduino
        self.resultadoNormal = sres
        self.resultadoAduino = self.filtrar(sres)
        self.contador = -1
        self.vel = 0

        # # IMPRIME LOS DETALLES DEL RESULTADO
        # salida = ''
        # for i in range(len(sres)):
        #     r = sres[i]
        #     if i/100==int(i/100):
        #         r=r+"\n"
        #     nres=nres+r
        # salida = salida+ 'LONGITUD DEL RESULTADO: '+str(len(sres))
        # salida = salida+ '\nRESULTADO: '+nres
        # self.resultastr = salida
        # self.resulta.set(self.resultastr)
        self.onUpdate()

    def calcelUpdate(self):
        if self._job is not None:
            self.master.after_cancel(self._job)
            self._job = None

    def onUpdate(self):
        self.calcelUpdate()
        # Actualiza el caracter enviado, la posición y el estado actual (pausa/play)
        self.contador = self.contador+1
        inicio = self.contador-self.porcionlen
        if inicio<0:
            inicio=0
        if self.contador>len(self.resultadoAduino)-2:
            enviar = '0'
        else:
            enviar = self.resultadoAduino[self.contador]
        self.porcion = self.porcion+enviar
        if len(self.porcion)>self.porcionlen-2:
            self.porcion = self.porcion[-self.porcionlen:]

        if self.debuguear>0:
            salida = u"Res: "+self.resultadoNormal[0:self.porcionlen]
            salida = salida+u"\nVelocidad: "+str(self.velist[self.vel])+" ms"
            salida = salida+u"\nPosición: "+str(self.contador)+" / "+str(len(self.resultadoAduino))
            salida = salida+u"\nDígito: "+enviar
            salida = salida+u"\nPorción: "+self.porcion.rjust(self.porcionlen, ' ').replace(' ','  ')
            self.resultastr = salida
            self.resulta.set(self.resultastr)
        # ENVIO A DISPLAY
        if self.sendToDisplay>0:
            arduino.write(enviar) # Envia digito actual a DISPLAY, la pausa la genera el unUpdate mismo
        # DEBUG EN CONSOLA
        if self.debuguear>0:
            print(current_iso8601(),self.contador,self.vel,self.velist[self.vel],enviar)
        # schedule timer para ayutollamarse cada segundo
        if self.vel>=0:
            self._job = self.master.after(self.velist[self.vel], self.onUpdate)

root = Tk()
calc = calculadora(root);
root.mainloop()