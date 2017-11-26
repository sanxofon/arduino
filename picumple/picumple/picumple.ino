String fecha = "311299"; // Fecha de ejemplo en formato DDMMAA (Solo fechas validas!)
int espera = 0;
void setup() {
    Serial.begin(9600); // debe coincidir con los baudios en el script python
}
void loop() {
    if (espera==0) {
        Serial.println(fecha); // Envia fecha de ejemplo a serial para python
        delay(100);
        espera=1; // espera antes de enviar una nueva fecha
    } else {
        if(Serial.available() > 0) {
            delay(100);
            espera=0; // si recibe cualquier respuesta en serial deja de esperar
        }
    }
}
