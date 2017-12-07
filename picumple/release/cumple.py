# coding: utf-8
# Author Santiago Chávez Novaro
# Busca tu cumpleaños en PI (π)

from Tkinter import Tk, Label, Canvas, StringVar, PhotoImage
import time, logging, datetime
import csv, re
from random import randint

# Log de uso
fechi = datetime.datetime.now()
logfile = fechi.strftime("%y%m")+".log"
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='log/'+logfile, level=logging.INFO)
logging.info("INFO\tInicio de programa")
"""
    CONTROLES ASIGNADOS:
         ______________________________________________
        |                                              |
        |  TECLAS ACEPTADAS:                           |
        |     0-9  => Numeros                          |
        |       i  => Enter                            |
        |       x  => Backspace                        |
        |       -----------------------                |
        |       k  => Salir del programa (oculto)      |
        |______________________________________________|
 
    INSTRUCCIONES:
        
        1. Definir VARIABLES GENERALES de Desarrollo o Producción en código (VER __init__ ABAJO)

        2. Ejecutar el programa con el acceso directo que se encuentra en la misma carpeta.
            2.1. Ejecutar desde consola para debug en carpeta:
                [WidowsKey]+R
                "cmd" + [ENTER]
                $ cd c:\Users\user\Ruta_ALaCarpeta\
                $ python cumple.py
        
        3. Iniciado el programa
            3.1. Escribir la fecha en el formato solicitado: DDMMAA y apretar ENTER (i)
            3.2. La fecha se buscará en PI y se recorrerá el número hasta el dígito adecuado

    BUGS:
        - DEBUG: No están dadas de alta las fechas inválidas, ej. 310299

"""
class cumple(object):
    def __init__(self):

        # DEFINIR VARIABLES GENERALES
        self.debuguear = 0          # Debug. Muestra en pantalla lo que se envia al display
        self.fullscreen = 1         # Abrir en pantalla completa. Dev: 0, Prd: 1

    def iniciar(self, master):
        ######### VARIABLES GENERALES #########
        self.velocidad = 1000 #Milisegundos
        self.vel = -1
        self.contador = -1
        self._job = None
        self.res = None
        self.maxtext = 6
        # CSV
        csv = self.open_csv("data/out1000.csv","\t")
        tags = csv.pop(0)
        lt = len(tags)
        lc = len(csv)
        # print lt,lc
        cumples = []
        for i in xrange(lc):
            c = {}
            for j in xrange(lt):
                c[tags[j]] = csv[i][j]
            cumples.append(c)
        self.cumples = cumples
        #######################################

        self.master = master
        self.master.configure(background='black')
        # self.master.wm_attributes('-transparentcolor','blue')

        if self.fullscreen>0:
            # Full screen
            master.overrideredirect(True)
            master.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
            master.focus_set()  # <-- move focus to this widget
            # Otra opción
            # master.attributes('-fullscreen', True)
        else:
            master.geometry("%dx%d+0+0" % (master.winfo_screenwidth()-16, master.winfo_screenheight()-80))

        master.title(u"Tu cumpleaños en PI")

        master.bind("<Escape>", lambda e: e.widget.quit()) # Python 2
        master.bind("<Key>", self.recibeChar)

        # Background MASCARILLA
        # C = Canvas(master, bg="black", height=root.winfo_screenheight(), width=root.winfo_screenwidth())
        # background_label = Label(master, image=bgfil)
        # background_label.place(x=0, y=0, relwidth=1, relheight=1)
        bgfil = PhotoImage(file = "bg.gif")
        bglabel = Label(master, image=bgfil)
        bglabel.place(x=0, y=0, relwidth=1, relheight=1)
        bglabel.image = bgfil

        # Posicion
        self.posistr = "" # "081284","230301"
        self.posi = StringVar()
        self.posi.set(self.posistr)
        self.labelpo = Label(master, textvariable=self.posi, bg="#000", fg="#eee", width=8, justify="left", font=("Roboto", 64))

        # DESPLIEGUE PI
        self.picustr = "3.1415"
        self.picu = StringVar()
        self.picu.set(self.picustr)
        self.labelp = Label(master, textvariable=self.picu, bg="#000", fg="#fff", width=self.maxtext+1, justify="center", font=("Anonymous Pro", 308))

        # FECHA INGRESADA
        self.fechastr = "" # "081284","230301"
        self.fecha = StringVar()
        self.fecha.set(self.fechastr)
        self.labelf = Label(master, textvariable=self.fecha, bg="black", fg="#eee", width=6, justify="center", font=("Roboto", 96))

        # Resultados extras
        self.resultastr = u"Ingresa tu fecha de cumpleaños: día, mes y año"
        self.resulta = StringVar()
        self.resulta.set(self.resultastr)
        self.labelr = Label(master, textvariable=self.resulta, bg="black", fg="#ccc", width=127, justify="left", font=("Roboto", 16))

        # Posiciona
        self.labelp.place(relx=0, rely=.22)
        self.labelpo.place(relx=0, rely=.07)
        self.labelf.place(relx=0.38, rely=.7)
        self.labelr.place(relx=0, rely=0)

        #######################################
        self.pi = '3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989'

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
        cadena = str(self.fechastr)

        # # Test input del teclado
        # self.resultastr = c+': ',str(k)+': '+str(event.state)
        # self.resulta.set(self.resultastr)
        # return
        
        self.resultastr = ''
        self.resulta.set(self.resultastr)

        numrs = ['0','1','2','3','4','5','6','7','8','9']
        posiciones = [
            ['0','1','2','3'],
            ['1','2','3','4','5','6','7','8','9'],
            ['0','1'],
            ['1','2','3','4','5','6','7','8','9'],
            numrs,
            numrs,
        ]
        # SALIDAS
        if c=='k': # k
            # salir del programa
            self.calcelUpdate()
            self.vel=-1
            self.cumple('SALIR', '')
            return
            # return '','SALIR'
        elif c=='c': # k
            # salir del programa
            self.calcelUpdate()
            self.velocidad=1000
            self.vel=-1
            self.picustr = "3.1415"
            self.picu.set(self.picustr)
            self.posistr = ""
            self.posi.set(self.posistr)
            self.fechastr = "" # "081284","230301"
            self.fecha.set(self.fechastr)
            self.resultastr = u"Ingresa tu fecha de cumpleaños: día, mes y año"
            self.resulta.set(self.resultastr)
            return
            # return '','SALIR'

        # IGUAL A
        elif k==10 or k==13 or c=='i':# or k==61: # [ENTER] o [=] > Salto de línea o igual: '\n' ó '\r' ó '='
            # imprimir cadena RESULTADO
            self.cumple('RESULTADO', cadena)
            return
            # return cadena,'RESULTADO'

        # ESCRITURA NORMAL
        elif k == 8 or c=='x': # BACKSPACE
            # recortar cadena un digito
            cadena = self.modcad(cadena,1)

        # NUMEROS DE INGRESO DE FECHA
        elif c in numrs: # NUMEROS 0-9
            # incrementa la cadena con c
            p = len(cadena)
            if p<6:
                a = ''
                if p>0:
                    a=cadena[-1:]
                if c in posiciones[p]:
                    if p==1:
                        if int(a)<3:
                            cadena = self.modcad(cadena,c)
                        elif int(c)<2:
                            cadena = self.modcad(cadena,c)
                    elif p==3:
                        if int(a)<1:
                            cadena = self.modcad(cadena,c)
                        elif int(c)<3:
                            cadena = self.modcad(cadena,c)
                    else:
                        cadena = self.modcad(cadena,c)
                if len(cadena)==p:
                    self.resultastr = u"Fecha inválida"
                    self.resulta.set(self.resultastr)
            else:
                self.resultastr = u"Aprieta Enter o ingresa otra fecha"
                self.resulta.set(self.resultastr)

        self.fechastr = cadena
        self.fecha.set(self.fechastr)


    def cumple(self, estado, cadena=''):
        if (estado=='RESULTADO'):
            self.calcelUpdate('Nuevo resultado')
            self.vel = -1 # Stop timer
            self.contador = -1 # Reset timer
            self.resultado(cadena)

        if (estado=='SALIR'):
            self.calcelUpdate()
            logging.info("INFO\tSalir del programa")
            time.sleep(1)
            self.vel = -1 # Stop timer
            self.master.quit()
            # return

    def open_csv(self,filename,csv_delimiter):
        data =[]
        with open(filename, 'rb') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=csv_delimiter, quotechar="'")
                for row in csvreader:
                        data.append(row)        
        return data
    def buscar(self,fecha):
        for i in xrange(len(self.cumples)):
            if (self.cumples[i]['s']==fecha):
                return self.cumples[i]
        return None

    def resultado(self, fec=''):
        self.calcelUpdate()
        self.fechastr = fec
        self.fecha.set(self.fechastr)
        self.resultastr = ""
        self.resulta.set(self.resultastr)
        self.velocidad=1000

        # RESULTADO COMO CADENA
        b = self.buscar(fec)
        if b is not None:
            self.res = b
            # salida = 'Fecha "%s" encontrada en la posicion "%d" de PI' % (fec,int(b['position']))
            # self.resultastr = salida
            # self.resulta.set(self.resultastr)
            logging.info("OK\t"+fec)
        else:
            self.resultastr = u"Fecha inválida"
            self.resulta.set(self.resultastr)
            logging.info("NOTFOUND\t"+fec)
            return
        # Set start envio Arduino
        self.contador = -1
        self.vel = 0
        # Inicia envío a display arduino
        self.onUpdate()

    def calcelUpdate(self,quien=''):
        if self._job is not None:
            if quien!='':
                logging.info("CANCEL\t"+quien)
            self.master.after_cancel(self._job)
            self._job = None

    def onUpdate(self):
        if self.vel==-1:
            return
        self.calcelUpdate()
        # Actualiza el caracter enviado, la posición y el estado actual (pausa/play)
        self.contador = self.contador+1
        pos = int(self.res['position'])

        # Condiciones de aceleración
        acel = 35
        maxpor = 100
        falta = pos-self.contador+7
        if falta<=0:
            self.vel=-1
        elif falta<acel+6:
            self.velocidad = int(self.velocidad*1.1)
        elif self.contador<acel:
            self.velocidad = int(self.velocidad/1.1)

        if self.contador<maxpor: #Inicio
            inicio = (self.contador-self.maxtext)
            if inicio<0:
                inicio = 0
            pipi = self.pi[inicio:self.contador].rjust(self.maxtext, ' ')
        elif falta<maxpor-6: # Final
            pipi = self.res['portion'][-falta-6:-falta]
            if falta<=0:
                pipi = self.fechastr
            print "pipi",pipi
        else: # Bogus intermedio
            pipi = str(randint(000000,999999))
            if falta>int(pos/2):
                self.contador = int(self.contador*1.05)
                if self.contador>int(pos/2):
                    self.contador = int(pos/2)+50
            elif falta<int(pos/4):
                self.contador = int(self.contador*1.001)
            elif falta<int(pos/2):
                self.contador = int(self.contador*1.01)
            if self.contador>pos-(maxpor-10):
                self.contador=pos-(maxpor-20)

        # Limites de velocidad
        if self.velocidad<30:
            self.velocidad=30
        if self.velocidad>1000:
            self.velocidad=1000

        self.picustr = pipi
        self.picu.set(self.picustr)
        posi = self.contador-7
        if posi>=-1:
            self.posistr = str(posi)
        else:
            self.posistr = ""
        self.posi.set(self.posistr)

        if self.debuguear>0:
            salida = u"PP: "+str(pos)+u"\tPosición: "+self.posistr+u"\tFalta: "+str(falta)+u"\tVelocidad: "+str(self.velocidad)
            # tiempofaltante = round(self.velist[self.vel]*(len(self.resultadoAduino)-self.contador)/1000)
            # m, s = divmod(tiempofaltante, 60)
            # h, m = divmod(m, 60)
            # salida = salida+u"\nTiempo restante: "+str("%d:%02d:%02d" % (h, m, s))+" hms"
            self.resultastr = salida
            self.resulta.set(self.resultastr)
        # schedule timer para ayutollamarse cada segundo
        if self.vel>=0:
            self._job = self.master.after(self.velocidad, self.onUpdate)


root = Tk()
cu = cumple();
cu.iniciar(root);
root.mainloop()