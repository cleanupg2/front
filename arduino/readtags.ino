#include <SPI.h>
#include <MFRC522.h>
#include <Keyboard.h>
 
#define SS_PIN 10
#define RST_PIN 9
 
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class MFRC522
 
MFRC522::MIFARE_Key key; 

// declares a string to store the UID of the last tag read by the sensor

String readData;

void setup() { 
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init RC522 
}
 
void loop() {
 
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if ( ! rfid.PICC_IsNewCardPresent())
    return;
 
  // Verify if the NUID has been read
  if ( ! rfid.PICC_ReadCardSerial())
    return;
 
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);

  //reads the tag's UID number: four pairs of HEX digits (pair of HEX digits = 4+4 bits or 1 byte), output by the mfrc lib in DEC
  //converts each pair back to HEX and attributes it to the readData string
  for (int i = 0; i < rfid.uid.size; i++) {
    String hexKey = "0123456789ABCDEF"; // key for the DEC to HEX conversion
    int working = int(rfid.uid.uidByte[i]); // auxiliary variable for the DEC to HEX conversion
    
    readData += hexKey[working/16];//first digit (16^1)
    readData += hexKey[working%16];//second digit (16^0)
    
    if (i < rfid.uid.size - 1) {//won't add a space after the last byte 
      readData += " "; 
    }
  }

  Serial.println(readData);


  // empties the UID-storing string for the next reading
  readData = "";
 
  rfid.PICC_HaltA(); // Halt PICC
}
