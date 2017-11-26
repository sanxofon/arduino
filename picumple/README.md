"Busca tu cumpleaños en PI"
======================

Permite buscar cualquier fecha válida en el formato DDMMAA dentro de los primeros 1G dígitos de PI.

---

## Dependencias:

 * [pySerial](http://pyserial.sourceforge.net)
 * Controlador Arduino

## Descripción de carpetas y archivos incluídos:

> En esta carpeta se guardan los archivos arduino

 - **/picumple** [arduino]
	 - **picumple.ino**
		 - Código arduino para testeo (sin funcionalidad de interfaz)

> En esta carpeta se guardan los archivos python

 - **/python**
	 - **/picumple.py** [servidor]
		 - Permite testear el dispositivo/interfaz *arduino*, recibe de este una fecha en formato *DDMMAA* y responde cuando la ha procesado (encontrado o no)
	 - **/logCumplePi.log**
		 - Archivo log de las entradas (fechas) recibidas, guarda la fecha recibida y la fecha actual separadas por comas
	 - **/testOnlyCom.py** [cliente *test only*]
		 - Permite testear el programa *picumple.py* sin necesidad de *arduino* por puerto serial. Deberá setearse la variable *arduinoON* en *picumple.py*
	 - **/data** [BD]
		 - **/out1000.csv**
		 	- Base de datos (CSV) de fechas en PI
		 - **/pi_1K.txt**
		 	- Primeros 1K dígitos de PI

> En esta carpeta se guardan los archivos demostrativos en formato HTML, JS, CSS *[standalone]*

 - **/demo** [HTML,JS,CSS]
	 - **[picumple.html](demo/picumple.html)**
		 * Standalone que permite ver el funcionamiento deseado de la interfaz y el despliegue final en simulación de LEDS o pantalla
	 - **[fechasDB.js](demo/fechasDB.js)**
		 * Javascript que contiene la BD de fechas y posiciones en PI

## Ejemplos de uso:

### PYTHON ONLY TEST
Para testear el código *picumple.py* sin necesidad de hacer las conexiones *arduino* se puede usar como cliente el código *testOnlyCom.py* y usar un software parecido a [com0com](https://sourceforge.net/projects/com0com) o [Virtual Serial Port Driver](http://www.eltima.com/products/vspdxp/) para conectar directamente los puertos: **COM2 <=> COM3**.

Debemos configurar la variable **arduinoON = False** en *picumple.py* para el modo testeo.

- Una vez hecho esto podemos ejecutar primero el servidor con:

            $ python picumple.py

	Dejamos abierta la terminal que quedará esperando por fechas en el puerto serial

- Ahora podemos ejecutar el cliente (en una terminal nueva) que enviará fechas al azar (algunas inválidas) en tiempos irregulares:

            $ python testOnlyCom.py

	Monitoreamos ambas terminales para ver cómo se comunican

### ARDUINO TEST
Para testear el código *picumple.py* desde *arduino* debemos conectarlo configurar el puerto y los baudios en las variables correspondientes dentro de los archivos: '/python/picumple.py' y '/picumple/picumple.ino'.

Debemos configurar la variable **arduinoON = True** en */picumple.py* para el modo arduino.

- Una vez hecho esto podemos ejecutar primero el servidor con:

            $ python picumple.py

	Dejamos abierta la terminal que quedará esperando por fechas en el puerto serial desde arduino

- Ahora podemos ejecutar el cliente desde arduino. Podemos usar el archivo de ejemplo: '/picumple/picumple.ino' y ver los resultados en la terminal python abierta.

###Desarrollo:

 * **Santiago Chávez** ([@sanxofon](http://twitter.com/sanxofon/), [sanxofon@gmail](mailto:sanxofon@gmail.com))

###License:

 * Apache License 2.0