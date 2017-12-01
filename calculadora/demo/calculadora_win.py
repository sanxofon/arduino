# coding: utf-8
from __future__ import division
from __future__ import print_function

from decimal import *
import readchar
import os,sys
from Tkinter import Tk, Label, Canvas, StringVar
from numericStringParser import *
from primefac import *
"""____________________________________________
|                                              |
|  TECLAS ACEPTADAS:                           |
|        0-9  => Numeros                       |
|          e  => Euler                         |
|          h  => Pi                            |
|          f  => Phi                           |
|          *  => Multiplicar                   |
|          +  => Sumar                         |
|          -  => Restar                        |
|          r  => Raiz cuadrada                 |
|          p  => Establecer dividendo          |
|          q  => Establecer divisor (dividir)  |
|     [ENTER] => Igual a                       |
|           c => Reiniciar                     |
|           k => Salir del programa            |
|____________________________________________"""

class calculadora(object):
    def __init__(self, master):
        self.master = master
        fullscreen = 0
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
        self.labelp = Label(master, textvariable=self.dividendo, bg="#fd0", width=21, justify="center", font=("Roboto", 96))

        self.line = Canvas(master, width=master.winfo_screenwidth(), height=50)
        # self.line.create_rectangle(0, 0, master.winfo_screenwidth(), 20, outline="#000", fill="#000")
        self.line.create_line(0, 0, master.winfo_screenwidth(), 0, fill="#000",width=50)

        # Divisor q
        self.divisorstr = "1"
        self.divisor = StringVar()
        self.divisor.set(self.divisorstr)
        self.labelq = Label(master, textvariable=self.divisor, bg="#eee", width=21, justify="center", font=("Roboto", 96))

        # Resultado res
        self.resultastr = ""
        self.resulta = StringVar()
        self.resulta.set(self.resultastr)
        self.labelr = Label(master, textvariable=self.resulta, bg="#eee", width=80, justify="left", font=("Roboto", 16))

        # Posiciona
        self.line.place(relx=0, rely=.495)
        self.labelp.place(relx=0, rely=.32)
        self.labelq.place(relx=0, rely=.545)
        self.labelr.place(relx=0, rely=.73)

        #######################################

        # self.operacion(p='',q=1)
        # self.calculadora()

        #######################################

    # Calcula la descomposicion en primos de un numero
    # regresa una lista con los factores primos y sus exponentes
    def primed(self, a):
        p, expo = 2, 0
        div = [[]]
        tmp = 0
        it = 0
        while p <= a:
            # print(("primed:",p,a),"\r")
            if a % p == 0:
                tmp = 1
                expo += 1
                a = a / p
                div[it] = [p,expo]
            else:
                if tmp ==1:
                    it +=1
                    div.append([ ])
                    tmp = 0
                p += 1
                expo = 0
        return div

    # multiplica con exponentes la lista y regresa el numero
    def multi(self, L):
        res = 1
        for a in L:
            res = res*a[0]**a[1]
        return res

    #Regresa el minimo comun multiplo de dos numeros
    #Si el resultado es [1,1] son primos relativos
    def mcm(self, a,b):
        A, B = self.primed(a), self.primed(b)
        mcc = []
        for a in A:
            for b in B:
                if a[0] == b[0]:
                    mcc.append([a[0], min(a[1],b[1])])
        if mcc == []:
            mcc = [1,1]
        return mcc


    # Aqui determina el periodo del denominador, si no tiene factores de 5 o de 2
    def mpl(self, q):
        if q%5 == 0 or q%2==0:
            return -1
        k = 0
        stop = True
        while stop:
            k +=1
            if (10**k-1) % q == 0:

                stop = False
        return k        

    ## Determina el periodo de una fraccion y lo comprueba
    def Periodo(self, q):
        # regresa: (i,j), donde i son los primeros y el periodo es j
        freQ, norep = [], [1]
        primeQ = self.primed(q)
        for a in primeQ:
            # OJO >> REVISAR SALIDA CUANDO NO HAY PUNTO FLOTANTE !!EXCEPCIÓN
            if len(a)<=0:
                return [0,0]
            if a[0]==2 or a[0]==5:
                norep.append(a[1])
            else:
                freQ.append(a)
        return [max(norep), self.mpl(self.multi(freQ))]
    
    def recibeChar(self,event):
        k = event.keycode
        c = event.char
        p = str(self.dividendostr)
        q = str(self.divisorstr)
        # self.resultastr = c+': '+str(k)
        # self.resulta.set(self.resultastr)
        # return
        if (self.dondestoy=='q'):
            cadena = q
            # if cadena=='1':
            #     cadena = ''
        else:
            cadena = p
        # SALIDAS
        if k == 67: # c
            # reiniciar programa
            self.calculadora('REINICIAR', '', p, q)
            return
            # return '','REINICIAR'
        elif k == 75: # k
            # salir del programa
            self.calculadora('SALIR', '', p, q)
            return
            # return '','SALIR'

        # IGUAL A
        elif k==10 or k==13:# or k==61: # [ENTER] o [=] > Salto de línea o igual: '\n' ó '\r' ó '='
            # imprimir cadena RESULTADO
            self.calculadora('RESULTADO', cadena, p, q)
            return
            # return cadena,'RESULTADO'

        # ESCRITURA NORMAL
        elif k == 8: # BACKSPACE
            # recortar cadena un digito
            if (len(cadena)>=1):
                cadena = cadena[:-1]
        elif (k>=48 and k<=57) or (k>=96 and k<=105): # NUMEROS 0-9
            # incrementa la cadena con c
            cadena = cadena+str(c)
        elif k==188 or k==190: # NUMEROS 0-9, COMA o PUNTO
            if k==188 or k==190:
                c='.' # Siempre usa punto
            # incrementa la cadena con c
            cadena = cadena+str(c)

        # NUMEROS ESPECIALES e y pi
        elif (k==69):    # e => 101
            # Euler's number => 'e'
            c = 'E'
            # incrementa la cadena con c
            cadena = cadena+str(c)
        elif (k==72):    # h => 104
            # PI => 'h'
            c = 'PI'
            # incrementa la cadena con c
            cadena = cadena+str(c)
        
        # OPERACIONES SIMPLES: * + - /
        elif (k==106 or k==186): # * => 42
            # incrementa la cadena con c
            cadena = cadena+str(c)
        elif (k==107 or k==187):    # + => 43
            # incrementa la cadena con c
            cadena = cadena+str(c)
        elif (k==109 or k==189):    # - => 45
            # incrementa la cadena con c
            cadena = cadena+str(c)
        elif (k==111 or k==191):    # / => 47
            # OPCION 1: incrementa la cadena con c ???
            # cadena = cadena+c
            # OPCION 2: Debe enviar al valor q sólo si no estamos ahí !!!???
            if (self.dondestoy!='q'):
                self.calculadora('SETQ', cadena, p, q)
                return
                # return cadena, 'SETQ'

        # DENOMINADORES P, Q
        elif (k==80):    # p => 112
            # Debe enviar al valor p sólo si no estamos ahí
            if (self.dondestoy!='p'):
                self.calculadora('SETP', cadena, p, q)
                return
                # return cadena, 'SETP'
        elif (k==81):    # q => 113
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
    
    def pausa(self, ):
        while 1:
            c = readchar.readchar()
            if c!='':
                break


    def calculadora(self, estado, cadena='', p='', q=''):
        if (estado=='RESULTADO'):
            if (self.dondestoy=='p'):
                p = cadena
            if (self.dondestoy=='q'):
                q = cadena
            if (q==''):
                q='1'
            nsp = NumericStringParser()
            res = nsp.eval(p+'/'+q)
            res = str(res)
            if (res[-2:]=='.0'):
                res=res[:-2]
            # res = p+'/'+q
            self.resultado(p,q, res)
            # self.pausa()
            # self.calculadora(cadena,p,q,dondestoy)
        if (estado=='REINICIAR'):
            self.operacion(p='',q=1)
            self.resultastr = ''
            self.resulta.set(self.resultastr)
            self.dondestoy = 'p'
            self.labelp.config(bg="#fd0")
            self.labelq.config(bg="#eee")
            # self.calculadora()
        if (estado=='SALIR'):
            self.master.quit()
            # return
        if (estado=='SETP'):
            q = cadena
            self.dondestoy = 'p'
            self.labelp.config(bg="#fd0")
            self.labelq.config(bg="#eee")
            # self.calculadora(p,p,q,dondestoy)
        if (estado=='SETQ'):
            p = cadena
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

    def resultado(self, p,q, res):
        ml,lp,lq = self.maxlen(p,q)
        self.dividendostr = str(p)
        self.dividendo.set(self.dividendostr)
        self.divisorstr = str(q)
        self.divisor.set(self.divisorstr)

        ################################################
        # Calcula p y q numericamente a floats
        nsp = NumericStringParser()
        fp = float(nsp.eval(p))
        fq = float(nsp.eval(q))
        # fp = Decimal(p)
        # fq = Decimal(q)
        # print fp,fq

        ################################################
        ####### AQUÍ VAN LOS CALCULOS DE PERIODO #######

        PL = self.Periodo(fq)
        # prec = (PL[0]+2)*(PL[1]+5)

        # self.resultastr = str(",".join([str(x) for x in PL]))
        # self.resulta.set(self.resultastr)
        # return

        prec = (PL[0]+2)*(PL[1]+5)
        getcontext().prec = prec

        # res = fp/fq
        res = Decimal(fp)/Decimal(fq)
        # self.resultastr = str(res)
        # self.resulta.set(self.resultastr)

        nrp, pl = PL[0], PL[1]
        cad = str(res).split('.')
        if len(cad)>1:
            precad = cad[0]
            cad = str(str(res).split('.')[1])
            repite = cad[nrp-1:pl+nrp-1]
        else: # No tiene decimales
            precad = ''
            cad = ''
            repite = ''


        salida = ''
        # # IMPRIME LOS DETALLES DEL PERIODO
        salida = salida+ 'LONGITUD DEL PERIODO: '+str(PL[1])
        salida = salida+ '\nPERIODO: '+str(repite)
        salida = salida+ '\nANTES DEL PERIODO: '+precad+'. '+str(cad[0:nrp-1])
        salida = salida+ '\nPRECISION: '+str(prec)
        salida = salida+ '\nRESULTADO: '+str(res)
        self.resultastr = str(salida)
        self.resulta.set(self.resultastr)

root = Tk()
calc = calculadora(root);
root.mainloop()