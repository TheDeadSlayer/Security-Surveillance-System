#include <Wire.h>
#include <Keypad.h>
#include <EEPROM.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>
#include <string.h>

#define mySerial Serial1

const byte numRows = 4;       //number of rows on the keypad
const byte numCols = 4;       //number of columns on the keypad

char keymap[numRows][numCols] =
{
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};


char keypressed;                 //Where the keys are stored it changes very often
String intialCode = "123456";    //The default code, you can change it or make it a 'n' digits one
String code = "123457";
String newCode="";

short a = 0, i = 0, s = 0, j = 0; //Variables used later
int fpflag=0;                     //Used to verify fingerprint
int rpflag=0;                     //Replace Flag
int delflag=0;                    //Delete Flag
int empflag=0;                    //Empty Flag

byte rowPins[numRows] = {39, 41, 43, 45}; //Rows 0 to 3 
byte colPins[numCols] = {47, 49, 51, 53}; //Columns 0 to 3

uint8_t id;                      //Fingerprint ID
uint8_t idArr[11];              //ID occurence flags


LiquidCrystal_I2C lcd(0x27, 16, 2);
Keypad myKeypad = Keypad(makeKeymap(keymap), rowPins, colPins, numRows, numCols);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);


void setup()
{
    Serial.begin(9600);
    finger.begin(57600);

    pinMode(10,INPUT);  // PUSH BUTTON
    pinMode(2,OUTPUT); // RELAY PIN 
    digitalWrite(2,HIGH); 
    
    // initialize the lcd
    lcd.init();                      
    lcd.backlight();
    lcd.begin (16, 2);
    lcd.setCursor(0, 0);
    lcd.print("Starting Systems");
    lcd.setCursor(1 , 1);
    delay(3000);
    lcd.clear();

    SetupCode();
    lcd.clear();
    lcd.print("*ENTER THE CODE*");
    lcd.setCursor(1 , 1);
    lcd.print("TO _/_ (Door)!!");      

    code=loadCode(0);
    newCode=loadCode(15);
    
    ExtractIDs();
}

void SetupCode()            //Intially Sets Passcode from database
{
    while(code==intialCode)
    {
        lcd.setCursor(5,0);
        lcd.print("Waiting");
        lcd.setCursor(4,1);
        lcd.print("for Setup");

        if (Serial.available() > 0) 
        {
            code = Serial.readStringUntil('.');
            newCode=code;
            storeCode(0,code);
            storeCode(15,newCode);
        }
    }

    Serial.println("Verify Code");
    delay(1000);
    
    if (Serial.available() > 0) 
        {
            code = Serial.readStringUntil('.');
            newCode=code;
            storeCode(0,code);
            storeCode(15,newCode);
        }

}

void storeCode(int addrOffset, const String &strToWrite)        //Store PassCode on EEPROM
{
    byte len = strToWrite.length();
    EEPROM.write(addrOffset, len);

    for (int i = 0; i < len; i++)
    {
        EEPROM.write(addrOffset + 1 + i, strToWrite[i]);
    }
}

String loadCode(int addrOffset)                               //Load PassCode from EEPROM
{
    int newStrLen = EEPROM.read(addrOffset);
    char data[newStrLen + 1];

    for (int i = 0; i < newStrLen; i++)
    {
        data[i] = EEPROM.read(addrOffset + 1 + i);
    }

    data[newStrLen] = '\0';
    return String(data);
}

void ExtractIDs()                           //Extract Occurences of IDs
{   
    empflag=0;
    for (int Fid = 1; Fid <=10; Fid++) 
    {
        uint8_t p = finger.loadModel(Fid);
        switch (p) 
        {
            case FINGERPRINT_OK:
                idArr[Fid]=1;break;
            default:
                idArr[Fid]=0;
        }

        if(idArr[Fid]==1)
            empflag=1;
        
        //Serial.print(idArr[Fid]);
    }
    //Serial.print("\n");
    // OK success!
}

void loop()
{
    keypressed = myKeypad.getKey();             //Constantly waiting for a key to be pressed

    if (digitalRead(10))                         //To unlock from inside using push button
    {                
        OpenDoor();
        delay(5000);
        CloseDoor();
        standby();
    }
  
    if (Serial.available() > 0)                //Constantly checking database for PassCode changes
        {
            newCode = Serial.readStringUntil('.');
            Serial.println("ACK");
        }

    if(newCode!=code)                         //Applying PassCode changes from database
        code=newCode;

    if (keypressed == '*')                    // * To input the code
    {                    
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.println("*ENTER THE CODE*");     //Message shown
        
        ReadCode();                         //The ReadCode function used to verify code is correct

        if (a == sizeof(code))        
        {
            if(empflag==0)                //If No fingerprints are stored 
            {
                lcd.clear();
                lcd.setCursor(0,0);
                lcd.print("Setup Fingerprnt");
                lcd.setCursor(0,1);
                lcd.print("A: Continue");
                fingerprint();                  
            }
        
            else                        //Fingerprint exists
            {
                lcd.clear();
                lcd.setCursor(5,0);
                lcd.print("Verify");
                lcd.setCursor(3,1);
                lcd.print("Fingerprint");
                fingerprint();                        
            }

            //Verfication complete , Access granted
            OpenDoor();
            delay(5000);
            CloseDoor();
        }
        
        else 
        {
            lcd.clear();
            lcd.setCursor(1, 0);
            lcd.print("CODE");      //Message to print when the code is wrong
            lcd.setCursor(6, 0);
            lcd.print("INCORRECT");
            lcd.setCursor(15, 1);
            lcd.print(" ");
            lcd.setCursor(4, 1);
            lcd.print("WALID!!!");
        }
        standby();
    }
}

void standby()   //Return to standby mode
{
    delay(3000);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("*ENTER THE CODE*");
    lcd.setCursor(1 , 1);
    lcd.print("TO _/_ (Door)!!");  
}

void ReadCode()             //Verifies Code
{                 
    i = 0;                    //All variables set to 0
    a = 0;
    j = 0;

    while (keypressed != 'A')                                 //The user press A to confirm the code otherwise he can keep typing
    {                                
        keypressed = myKeypad.getKey();
        if (keypressed != NO_KEY && keypressed != 'A' )           //If the char typed isn't A and neither "nothing"
        {         
            lcd.setCursor(j, 1);                                 //This to write "*" on the LCD whenever a key is pressed it's position is controlled by j
            lcd.print(keypressed); //Change to *
            j++;

            if (keypressed == code[i] && i < sizeof(code))      //if the char typed is correct a and i increments to verify the next caracter
            {       
                a++;
                i++;
            }
            else
                a--;                                               //if the character typed is wrong a decrements and cannot equal the size of code []
        }
    }

    keypressed = NO_KEY;
}


void fingerprint()              //Fingerprint Functions
{
    while (fpflag==0)
    {
        getFingerprintIDez();                 //Function for verifying fingerprints stored in memory
        keypressed = myKeypad.getKey();      //Reading the buttons typed by the keypad

        if(keypressed == 'A')                //If it's 'A' new fingerprints can be added
        {              
            Enrolling();                      //Enrolling function
            lcd.clear();
            lcd.setCursor(5,0);
            lcd.print("Verify");
            lcd.setCursor(3,1);
            lcd.print("Fingerprint");
        }

    if(keypressed == 'D')                //If it's 'D' delete fingerprints
        {              
            lcd.clear();
            lcd.setCursor(0,0);
            lcd.print("Type ID to Del");
            deleteFinger();
            lcd.clear();
            lcd.setCursor(5,0);
            lcd.print("Verify");
            lcd.setCursor(3,1);
            lcd.print("Fingerprint");
        }
    }

  fpflag=0;
}

int getFingerprintIDez()       // Gets fingerprint IDs (Default function)
{
    uint8_t p = finger.getImage();        //Image scanning
    if (p != FINGERPRINT_OK)  return -1;  

    p = finger.image2Tz();               //Converting
    if (p != FINGERPRINT_OK)  return -1;

    p = finger.fingerFastSearch();     //Looking for matches in the internal memory

    if (p != FINGERPRINT_OK)           //if the searching fails it means that the template isn't registered
    {          
        lcd.clear();                     //And here we write a message or take an action for the denied template
        lcd.print("Access denied");
        delay(2000);
        lcd.clear();
        lcd.setCursor(5,0);
        lcd.print("Verify");
        lcd.setCursor(3,1);
        lcd.print("Fingerprint");
        return -1;
    }

    //If we found a match we proceed in the function
  
    lcd.clear();
    lcd.print("Welcome");        //Printing a message for the recognized template
    lcd.setCursor(2,1);
    lcd.print("ID: ");
    lcd.setCursor(5,1);
    lcd.print(finger.fingerID); //And the ID of the finger template
    delay(2000);

    fpflag=1;
    return fpflag; 
}

void Enrolling()              //Enrolling new fingerprints and replacing enrolled ones 
{
    rpflag=0;
    keypressed = NULL;
  
    lcd.clear();
    lcd.print("Enroll New");
    delay(2000);
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Enter new ID");
    id = readnumber();                           //This function gets the Id it was meant to get it from the Serial monitor but we modified it
  
    if (id>10 || id<1) 
    {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("ID out of range");
        delay(2000);
        return;
    }

    lcd.clear();
    keypressed=NULL;

    for(int fid=1;fid<=10;fid++)
    {
        if (idArr[fid]==1 && id==fid)
            rpflag=1;
    }

    if(rpflag==1)
    {
        while(keypressed!='A')
        {
        
            lcd.setCursor(0,0);
            lcd.print("Replace?");
            lcd.setCursor(0,1);
            lcd.print("A:Yes  B:No");
            keypressed = myKeypad.waitForKey(); 

            if(keypressed=='B')
                return;
        }
    }

    while (!  getFingerprintEnroll() );
    ExtractIDs();
}

void deleteFinger()             //Delete Fingerprint
{
    delflag=0;
    id = readnumber();                           //Gets ID from user

    if (id>10 || id<1) 
    {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("ID out of range");
        delay(2000);
        return;
    }

    keypressed = NULL;
    for(int fid=1;fid<=10;fid++)
    {
        if (idArr[fid]==1 && id==fid)
            delflag=1;
    }
  
    if(delflag==1)
    { 
        lcd.clear();
        while(keypressed!='A')
        {
            lcd.setCursor(0,0);
            lcd.print("Delete?");
            lcd.setCursor(0,1);
            lcd.print("A:Yes  B:No");
            keypressed = myKeypad.waitForKey(); 
        
            if(keypressed=='B')
                return;
        }
        
        finger.deleteModel(id);
        lcd.clear();
        lcd.setCursor(5,0);
        lcd.print("Deleted");
        delay(1500);
   }
   else
   {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Not Found!!");
        lcd.setCursor(0,1);
        lcd.print("Returning...");
        delay(1500);
        return;
   }

   ExtractIDs();
   if(empflag==0)                //If No fingerprints are stored 
   {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Setup Fingerprnt");
        lcd.setCursor(0,1);
        lcd.print("A: Continue");
        fingerprint();                  
   }
}

uint8_t readnumber(void)   //Function for inputing fingerprint ID
{
    uint8_t num = 0;
    char idTemp[20];
    int k=0;
    while (keypressed!='A') 
    {
        keypressed = myKeypad.waitForKey(); 
        idTemp[k]= keypressed;
        lcd.setCursor(k,1);
        lcd.print(idTemp[k]);
        k++;
    }

    int temp =atoi(idTemp);
    num=temp;
    return num;
}

uint8_t getFingerprintEnroll()  //Fingerprint Enrolling function (Default function)
{
    int p = -1;
    lcd.clear();
    lcd.print("Enroll ID:"); //Message to print for every step
    lcd.setCursor(10,0);
    lcd.print(id);
    lcd.setCursor(0,1);
    lcd.print("Set Fingerprint");

    while (p != FINGERPRINT_OK){
        p = finger.getImage();
    }
        // OK success!

    p = finger.image2Tz(1);
  
    switch (p) 
    {
        case FINGERPRINT_OK:
            break;
        case FINGERPRINT_IMAGEMESS:
            return p;
        case FINGERPRINT_PACKETRECIEVEERR:
            return p;
        case FINGERPRINT_FEATUREFAIL:
            return p;
        case FINGERPRINT_INVALIDIMAGE:
            return p;
        default:
            return p;
    }
  
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Remove Finger"); //After getting the first template successfully
    lcd.setCursor(0,1);
    lcd.print("Please !");
    delay(2000);

    p = 0;
    while (p != FINGERPRINT_NOFINGER) {
        p = finger.getImage();
    }

    p = -1;
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Place Same"); //We launch the same thing another time to get a second template of the same finger
    lcd.setCursor(0,1);
    lcd.print("Finger Please");

    while (p != FINGERPRINT_OK) {
        p = finger.getImage();
    }
        // OK success!

    p = finger.image2Tz(2);

    switch (p) 
    {
        case FINGERPRINT_OK:
            break;
        case FINGERPRINT_IMAGEMESS:
            return p;
        case FINGERPRINT_PACKETRECIEVEERR:
            return p;
        case FINGERPRINT_FEATUREFAIL:
            return p;
        case FINGERPRINT_INVALIDIMAGE:
            return p;
        default:
            return p;
    }
  
    p = finger.createModel();

    if (p == FINGERPRINT_OK) {
    } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
        return p;
    } else if (p == FINGERPRINT_ENROLLMISMATCH) {
        return p;
    } else {
        return p;
    }   
  
    p = finger.storeModel(id);

    if (p == FINGERPRINT_OK) 
    {
        lcd.clear();                //if both images are similar, fingerprint is stored
        lcd.setCursor(0,0);
        lcd.print("Stored in");    //Print a message showing ID of stored fingerprint
        lcd.setCursor(0,1);
        lcd.print("ID: ");
        lcd.setCursor(5,1);
        lcd.print(id);
        delay(2000);

    } else if (p == FINGERPRINT_PACKETRECIEVEERR) {
        return p;
    } else if (p == FINGERPRINT_BADLOCATION) {
        return p;
    } else if (p == FINGERPRINT_FLASHERR) {
        return p;
    } else {
        return p;
    }   
}

void OpenDoor()           //Lock opening function open for 5s 
{            
    lcd.clear();
    lcd.setCursor(1, 0);
    lcd.print("Access Granted");
    lcd.setCursor(4, 1);
    lcd.print("WELCOME!!");
    digitalWrite(2,LOW); 
}

void CloseDoor()        //Closes Lock 
{
    lcd.clear();
    lcd.setCursor(1, 0);
    lcd.print("Closing...");
    digitalWrite(2,HIGH); 
}
