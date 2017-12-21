# coding: utf-8
import csv, time, serial
import re
import codecs,locale,sys
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)
# python picumple.py
# ARDUINO CONFIG ------------------------
arduinoON = True # PYTHON ONLY TEST: False, ARDUINO ON: True
if arduinoON:
    arduino = serial.Serial('COM11', 9600, timeout=.1) # debe coincidir con los baudios y el puerto arduino

def open_csv(filename,csv_delimiter):
        data =[]
        with open(filename, 'rb') as csvfile:
                csvreader = csv.reader(csvfile, delimiter=csv_delimiter, quotechar="'")
                for row in csvreader:
                        data.append(row)        
        return data
csv = open_csv("data/out1000.csv","\t")
tags = csv[0]
csv.pop(0)
lt = len(tags)
lc = len(csv)
# print lc

cumples = []
for i in xrange(lc):
    c = {}
    for j in xrange(lt):
        c[tags[j]] = csv[i][j]
    cumples.append(c)
def buscar(fecha):
    global cumples
    for i in xrange(len(cumples)):
        if (cumples[i]['s']==fecha):
            return cumples[i]
    return None

def logDatos(datos):
    with open("logCumplePi.log", "a") as myfile:
        myfile.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())+','+datos+"\n")

print u"Esperando fecha en puerto serial..."
while True:

    # ARDUINO -------------------------------
    # fecha = arduino.readline()[:-2] #capturamos la fecha y eliminamos el salto de linea final
    if arduinoON:
        fecha = arduino.readline() #capturamos la fecha
    # else:
    #     # Test only
    #     time.sleep(10)
    #     fecha = '240475' 

    if fecha:
        # print 'FECHA:',fecha

        # ARDUINO -------------------------------
        # time.sleep(1) # darle un segundo a arduino

        r = re.compile(r"^([0-2][0-9]|3[0-1])(0[0-9]|1[0-2])([0-9][0-9])$")
        fecha = fecha.strip()
        m = r.match(fecha)
        if m is not None: # comprobamos el formato de la cadena numerica
            # print '<',fecha
            fechaprint = m.group(1)+'/'+m.group(2)+'/'+m.group(3)
            b = buscar(fecha)
            if b is not None:
                datos = u'Fecha "%s" encontrada en la posición "%d" de PI' % (fechaprint,int(b['position']))
                logDatos(fechaprint+','+b['position'])
                print(datos)
                print(b)
                # print b

                # ARDUINO -------------------------------
                if arduinoON:
                    arduino.write(b['position']) # enviamos 'position' como respuesta correcta
                # arduino.write(",".join(b.values())) # podemos devolver todos los datos a arduino pero no es el caso arduino no interpretará la respuesta
                # break
            else:
                datos = u'Fecha inválida: "%s"' % fechaprint
                logDatos(fechaprint+',NOTFOUND')
                print(datos)
                # ARDUINO -------------------------------
                if arduinoON:
                    arduino.write("ERROR1") # enviamos 'ERROR' como error
        else:
            datos = u'ERROR: Fecha "%s" inválida' % fechaprint
            logDatos(fechaprint+',INVALID')
            print(datos)
            # ARDUINO -------------------------------
            if arduinoON:
                arduino.write("ERROR2") # enviamos 'ERROR' como error
        

        # break

# ARDUINO -------------------------------
if arduinoON:
    arduino.write("FIN") # enviamos 'ERR' para avisar a arduino que terminamos