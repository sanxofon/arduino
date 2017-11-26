# coding: utf-8
import csv, time, serial

# ARDUINO CONFIG ------------------------
arduinoON = True # PYTHON ONLY TEST: False, ARDUINO ON: True
arduino = serial.Serial('COM2', 9600, timeout=.1) # debe coincidir con los baudios y el puerto arduino

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

print "Esperando fecha en puerto serial..."
while True:

	# ARDUINO -------------------------------
	# fecha = arduino.readline()[:-2] #capturamos la fecha y eliminamos el salto de linea final
	fecha = arduino.readline() #capturamos la fecha
		
	if fecha:
		# print 'FECHA:',fecha

		# ARDUINO -------------------------------
		time.sleep(1) # darle un segundo a arduino

		import re
		r = re.compile('^([0-2][0-9]|3[0-1])(0[0-9]|1[0-2])([0-9][0-9])$')
		m = r.match(fecha)
		if m is not None: # comprobamos el formato de la cadena numerica
			# print '<',fecha
			fechaprint = m.group(1)+'/'+m.group(2)+'/'+m.group(3)
			b = buscar(fecha)
			if b is not None:
				datos = 'Fecha "%s" encontrada en la posicion "%d" de PI' % (fechaprint,int(b['position']))
				logDatos(fechaprint+','+b['position'])
				print(datos)
				# print b

				# ARDUINO -------------------------------
				arduino.write(b['position']) # enviamos 'position' como respuesta correcta
				# arduino.write(",".join(b.values())) # podemos devolver todos los datos a arduino pero no es el caso arduino no interpretará la respuesta
				# break
			else:
				datos = 'ERROR: Fecha "%s" no encontrada' % fechaprint
				logDatos(fechaprint+',NOTFOUND')
				print(datos)
				# ARDUINO -------------------------------
				arduino.write("ERROR1") # enviamos 'ERROR' como error
		else:
			datos = 'ERROR: Fecha "%s" invalida' % fechaprint
			logDatos(fechaprint+',INVALID')
			print(datos)
			# ARDUINO -------------------------------
			arduino.write("ERROR2") # enviamos 'ERROR' como error
		

		# break

# ARDUINO -------------------------------
arduino.write("FIN") # enviamos 'ERR' para avisar a arduino que terminamos