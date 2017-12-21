String fecha = ""; // Fecha de ejemplo en formato DDMMAA (Solo fechas validas!)
int ledPin = 9;
int espera = 0;
void setup() {
    pinMode(ledPin, OUTPUT);
    Serial.begin(9600); // debe coincidir con los baudios en el script python
}
void loop() {
    if (espera==0) {
        fecha = String(random(0, 3))+String(random(0, 9))+String(random(0, 1))+String(random(0, 9))+String(random(0, 9))+String(random(0, 9));
        Serial.println(fecha); // Envia fecha de ejemplo a serial para python
        digitalWrite(ledPin, HIGH);   // turn the LED on (HIGH is the voltage level)
        digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
        delay(500);
        digitalWrite(ledPin, LOW);   // turn the LED on (LOW is the voltage level)
        digitalWrite(LED_BUILTIN, LOW);   // turn the LED on (LOW is the voltage level)
        delay(random(1000, 15000));
        espera=1; // espera antes de enviar una nueva fecha
    } else {
        if(Serial.available() > 0) {
            delay(100);
            espera=0; // si recibe cualquier respuesta en serial deja de esperar
        }
    }
}
