// =======================================================================================
//                              Arduino Robot Controller
// =======================================================================================
//                          Last Revised Date: 12/14/2024
//                             Revised By: Prof McLaughlin
// =======================================================================================
// ---------------------------------------------------------------------------------------
//                          Libraries
// ---------------------------------------------------------------------------------------
#include <Sabertooth.h>
#include <Adafruit_TLC5947.h>
#include <DYPlayerArduino.h>
#include <Servo.h> 
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <math.h>

#define sign(x) ((x) < 0 ? -1 : 1)
#define I2C_ADDRESS 0x08  // I2C address for the Arduino Mega 
#define SABERTOOTH_ADDR 128
String I2CInboundString = ""; // Buffer for storing the received data
int driveDeadBandRange = 10;
Sabertooth *ST=new Sabertooth(SABERTOOTH_ADDR, Serial1); //TX1 – Pin#18

int currSpeed = 0;
int currTurn = 0;
boolean robotMoving = false;
boolean autonomous = true;

// ---------------------------------------------------------------------------------------
//    Request State Machine Variables for PS5 Controller
// ---------------------------------------------------------------------------------------
// Main flag to see if the PS5 Controller is sending data
boolean PS5ControllerLive = true;
//PS5ControllerLive = true;

// Main state varable to determine if a request has been made by the PS3 Controller
boolean reqMade = false;
boolean reqLeftJoyMade = false;
boolean reqRightJoyMade = false;

// LEFT & RIGHT Joystick State Request Values
boolean reqLeftJoyUp = false;
boolean reqLeftJoyDown = false;
int reqLeftJoyYValue = 0;

boolean reqLeftJoyLeft = false;
boolean reqLeftJoyRight = false;
int reqLeftJoyXValue = 0;

boolean reqRightJoyUp = false;
boolean reqRightJoyDown = false;
int reqRightJoyYValue = 0;

boolean reqRightJoyLeft = false;
boolean reqRightJoyRight = false;
int reqRightJoyXValue = 0;

// PS3 Controller Button State Variables
boolean reqArrowUp = false;
boolean reqArrowDown = false;
boolean reqArrowLeft = false;
boolean reqArrowRight = false;
boolean reqCircle = false;
boolean reqCross = false;
boolean reqTriangle = false;
boolean reqSquare = false;
boolean reqL1 = false;
boolean reqL2 = false;
boolean reqR1 = false;
boolean reqR2 = false;
boolean reqShare = false;
boolean reqOptions = false;
boolean reqPS = false;
boolean reqJSLeftButton = false;
boolean reqJSRightButton = false;

String command;
boolean commandRecieved = false;

Servo myServo;

// ---------------------------------------------------------------------------------------
//    Used for Pin 13 Main Loop Blinker
// ---------------------------------------------------------------------------------------
long blinkMillis = millis(); // absolute time
boolean blinkOn = false;

// ---------------------------------------------------------------------------------------
//    Timer Controller Variable
// ---------------------------------------------------------------------------------------
long currentTime = millis();

// =======================================================================================
//                                 Main Program
// =======================================================================================
// =======================================================================================
//                                Setup Function
// =======================================================================================
void setup() {
  
  //Initialize Serial @ 115200 baud rate for Serial Monitor Debugging
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("Arduino Robot Controller Started");

  //Start I2C communication for PS5 controller data channel from Raspberry Pi
  Wire.begin(I2C_ADDRESS);  // Initialize the Arduino as an I2C slave
  Wire.onReceive(receivePS5Data); // Register the receive event handler

  //Start Serial3 for all non-PS5 messages from the Raspberry Pi
  Serial3.begin(115200);
  while (!Serial3);
  
  //Setup PIN 13 for Arduino Main Loop Blinker Routine
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);

  // ----------------------------------------------
  // YOUR SETUP CONTROL CODE SHOULD START HERE
  // ----------------------------------------------

  myServo.attach(9);
//  myServo.write(90);
//  currServoPos = 90;

  Serial1.begin(9600); //Start TX1 – Pin#18 – Motor Controller
  ST->autobaud();
  ST->setTimeout(200);
  ST->setDeadband(driveDeadBandRange);

  // ----------------------------------------------
  // YOUR SETUP CONTROL CODE SHOULD END HERE
  // ---------------------------------------------
}

// =======================================================================================
//    Main Program Loop - This is the recurring check loop for entire sketch
// =======================================================================================
void loop()
{   
   currentTime = millis();

   check_inbound_serial_message();

   // If the PS5 controller is sending data - start processing the main controller routines
    if (PS5ControllerLive) {

      // ----------------------------------------------
      // YOUR MAIN LOOP CONTROL CODE SHOULD START HERE
      // ----------------------------------------------
      if (autonomous){
        decide();
      } else {
        moveRobot2();
      }

	    // checkServo();
       // Sample droid function call from PS5 request - REMOVE ONCE YOU UNDERSTAND STRUCTURE
       if (reqCross) {
          cross(ST);
       }
       if (reqCircle) {
         circle(ST);
       }
       if (reqTriangle) {
         triangle(ST);
       }
       if (reqSquare) {
         square(ST);
       }
    
       // ----------------------------------------------
       // YOUR MAIN LOOP CONTROL CODE SHOULD END HERE
       // ----------------------------------------------
      
       // If there was a PS5 request this loop - reset the request variables for next loop
       if (reqMade) {
           resetRequestVariables();
           reqMade = false;
       } 
   }

   // Blink to show working heart beat on the Arduino control board
   // If Arduino LED is not blinking - the sketch has crashed
   if ((blinkMillis + 500) < currentTime) {
      if (blinkOn) {
        digitalWrite(13, LOW);
        blinkOn = false;
      } else {
        digitalWrite(13, HIGH);
        blinkOn = true;
      }
      blinkMillis = millis();
   }
}

// =======================================================================================
//      ADD YOUR CUSTOM DROID FUNCTIONS STARTING HERE
// =======================================================================================
int deltaSpeed(int currSpeed, int targetSpeed, double acceleration) {
  if (currSpeed == targetSpeed) {
      return 0;  // No change needed
  }
  int speedDiff = targetSpeed - currSpeed;
  int step = (int)(acceleration * abs(speedDiff)); // Ensure gradual acceleration
  if (step < 1) step = 1; // Prevent being stuck when acceleration is too low
  if (abs(speedDiff) <= step) {
      return speedDiff;  // Directly reach target if within step size
  }
  return (speedDiff > 0) ? step : -step;  // Increment or decrement gradually
}

int rampTurn(int target){
  return (int)(target/2);
}
int rampForward(int target, int curr){
//  if (target>0){
//    return (int)(log(target));
//  }
  return (int)(target/2);
}

void moveRobot2() {
  if (reqLeftJoyMade) {
      currSpeed += deltaSpeed(currSpeed, reqLeftJoyYValue/1.5, 0.01);
      currTurn = reqLeftJoyXValue/3; //deltaSpeed(currTurn, reqLeftJoyXValue/2, 0.001);
      ST->turn(currTurn);
      ST->drive(-currSpeed);
      robotMoving = true;
  } else if (robotMoving) {// Smooth deceleration when joystick is released
      currSpeed += deltaSpeed(currSpeed, 0, 0.02);
      currTurn = 0;//deltaSpeed(currTurn, 0, 0.02);
      if (abs(currSpeed) > 0 || abs(currTurn) > 0) {
          ST->drive(-currSpeed);
          ST->turn(currTurn);
      } else {// Fully stop the robot when speed and turn reach zero
          ST->stop();
          currSpeed = 0;
          currTurn = 0;
          robotMoving = false;
      }
  }
  Serial.println("Speed: "+currSpeed);
}

void moveRobot() {
  if (reqLeftJoyMade) {
      currSpeed = rampForward(reqLeftJoyYValue, currSpeed);
      currTurn = rampTurn(reqLeftJoyXValue);
      ST->turn(currTurn);
      ST->drive(currSpeed*-1);
      robotMoving = true;
  } 
  else {
    if (robotMoving){
        ST->stop();
        currSpeed = 0;
        currTurn = 0;
        robotMoving = false;
    }
  }
}

void decide(){
  if (commandRecieved){
    if (command=="LEFT"){
      Serial.println("left");
      turn(ST,command);
    } else if (command=="RIGHT"){
      Serial.println("right");
      turn(ST,command);
    } else if (command=="STOP"){
      Serial.println("stop");
      stop(ST);
    } else if (command=="FORWARD"){
      Serial.println("forward");
      drive(ST);
    }
  }
  command = "";
  commandRecieved = false;
}

void moveForward(Sabertooth* ST, int speed) {
  ST->drive(speed);
}

void turnLeft(Sabertooth* ST, int speed) {
  ST->turn(-speed);
}

void turnRight(Sabertooth* ST, int speed) {
  ST->turn(speed);
}

void stop(Sabertooth* ST) {
  ST->drive(0);
  ST->turn(0);
}

void drive(Sabertooth* ST){
  const int MOVE_SPEED = 60;
  const int FORWARD_TIME = 150;
  for (int i = 0; i<10; i++){
    moveForward(ST, MOVE_SPEED);
    delay(FORWARD_TIME);
  }
  stop(ST);
}

void turn(Sabertooth* ST, String direction) {
  const int MOVE_SPEED = 60;        // Speed for moving (0-127)
  const int TURN_SPEED = 51;        // Speed for turning (0-127)
  const int FORWARD_TIME = 150;    // Time to move forward ~1 foot (milliseconds)
  const int TURN_TIME = 150;        // Time for approximately 90 degree turn (milliseconds)
  
  // First move forward one foot
  for (int i = 0; i<10; i++){
    moveForward(ST, MOVE_SPEED);
    delay(FORWARD_TIME);
  }
  stop(ST);
  delay(100);  // Brief pause after moving
  
  // Then turn based on command
  if (direction == "LEFT") {
    for (int i = 0; i<6; i++){
       turnLeft(ST, TURN_SPEED+6);
       delay(TURN_TIME); 
    }
    stop(ST);
  } 
  else if (direction == "RIGHT") {
    for (int i = 0; i<7; i++){
       turnRight(ST, TURN_SPEED);
       delay(TURN_TIME); 
    }
    stop(ST);
  }
}

//void checkServo(){
//	// if(reqArrowUp && currServoPos!=140){
//	// 	myServo.write(140);
//	// 	currServoPos = 140;
//	// }
//	if (reqLeftJoyLeft || reqLeftJoyRight) && !servoRoutineInitialized){
//		servoMillis = millis();
//		servoMoving = true;
//		servoRoutineInitialized = true;
//	}
//  //left
//	if(reqLeftJoyLeft && (servoMillis+50 < millis()) && servoRoutineInitialized){
//		if(currServoPos < 140){
//			currServoPos = min(currServoPos + 15,140);
//			myServo.write(currServoPos);
//			servoMillis = millis();

void circle(Sabertooth* ST){
//    myServo.write(0);
  turn(ST,"RIGHT");
}
void square(Sabertooth* ST){
//    myServo.write(140);
  turn(ST,"LEFT");
}
void cross(Sabertooth* ST){
  stop(ST);
}
void triangle(Sabertooth* ST){
  drive(ST);
}
void leftJoyDown(){
  myServo.write(max(0,min(reqLeftJoyYValue,140)));
}
void leftJoyUp(){
  myServo.write(max(min(reqLeftJoyYValue,140),0));
}
void leftJoyLeft(){
//  myServo.write(reqLeftJoyXValue);
}
void leftJoyRight(){
//  myServo.write(reqLeftJoyXValue);
}

// =======================================================================================
//      YOUR CUSTOM DROID FUNCTIONS SHOULD END HERE
// =======================================================================================

// =======================================================================================
//      CORE DROID CONTROL FUNCTIONS START HERE - EDIT WITH CAUTION
// =======================================================================================
// Process the PS5 Controller request from Raspberry Pi and set request state variables
void setPS5Request(String PS5Request)
{    
     if (PS5Request.substring(0,1) == "J") {
        if (PS5Request.substring(1,2) == "L") {
          reqLeftJoyXValue = PS5Request.substring(3,6).toInt();
          reqLeftJoyYValue = PS5Request.substring(8,11).toInt();
          
          if (PS5Request.substring(2,3) == "-") {
              reqLeftJoyXValue = reqLeftJoyXValue * -1;
          }
          if (PS5Request.substring(7,8) == "-") {
              reqLeftJoyYValue = reqLeftJoyYValue * -1;
          }
        }
      
        if (PS5Request.substring(1,2) == "R") {
          reqRightJoyXValue = PS5Request.substring(3,6).toInt();
          reqRightJoyYValue = PS5Request.substring(8,11).toInt();
          if (PS5Request.substring(2,3) == "-") {
              reqRightJoyXValue = reqRightJoyXValue * -1;
          }
          if (PS5Request.substring(7,8) == "-") {
              reqRightJoyYValue = reqRightJoyYValue * -1;
          }
        }

        PS5Request = PS5Request.substring(0,2);
     }

     if (PS5Request == "BTN13")
     {              
            Serial.println("Button: Arrow UP Selected");   
            reqArrowUp = true;
            reqMade = true;                
     }
  
  
     if (PS5Request == "BTN14")
     {
            Serial.println("Button: Arrow DOWN Selected");
            reqArrowDown = true;
            reqMade = true;           
     }

     if (PS5Request == "BTN15")
     {
            Serial.println("Button: Arrow LEFT Selected");
            reqArrowLeft = true;
            reqMade = true;
     }
     
     if (PS5Request == "BTN16")
     {
            Serial.println("Button: Arrow RIGHT Selected");

            reqArrowRight = true;
            reqMade = true;
     }
     
     if (PS5Request == "BTN01")
     {
            Serial.println("Button: CIRCLE Selected");
            reqCircle = true;
            reqMade = true;
     }

     if (PS5Request == "BTN00")
     {
            Serial.println("Button: CROSS Selected");
            reqCross = true;
            reqMade = true;
     }
     
     if (PS5Request == "BTN02")
     {
            Serial.println("Button: TRIANGLE Selected");
            reqTriangle = true;
            reqMade = true;
     }
     

     if (PS5Request == "BTN03")
     {
            Serial.println("Button: SQUARE Selected");
            reqSquare = true;
            reqMade = true;
     }
     
     if (PS5Request == "BTN04")
     {
            Serial.println("Button: LEFT 1 Selected");
            reqL1 = true;
            reqMade = true;
     }

     if (PS5Request == "BTN06")
     {
            Serial.println("Button: LEFT 2 Selected");
            reqL2 = true;
            reqMade = true;
     }

     if (PS5Request == "BTN05")
     {
            Serial.println("Button: RIGHT 1 Selected");
            reqR1 = true;
            reqMade = true;
     }

     if (PS5Request == "BTN07")
     {
            Serial.println("Button: RIGHT 2 Selected");
            reqR2 = true;
            reqMade = true;
     }

     if (PS5Request == "BTN08")
     {
            Serial.println("Button: Share Selected");
            reqShare = true;
            reqMade = true;
     }

     if (PS5Request == "BTN09")
     {
            Serial.println("Button: Options Selected");
            reqOptions = true;
            reqMade = true;

     }

     if (PS5Request == "BTN10")
     {
            Serial.println("Button: PS Selected");
            reqPS = true;
            reqMade = true;
     }

     if (PS5Request == "BTN11")
     {
            Serial.println("Button: Left Joystick Button Selected");
            reqJSLeftButton = true;
            reqMade = true;
     }

     if (PS5Request == "BTN12")
     {
            Serial.println("Button: Right Joystick Button Selected");
            reqJSRightButton = true;
            reqMade = true;
     }

     if (PS5Request == "JL")
     {    
            reqLeftJoyUp = false;
            reqLeftJoyDown = false;
            reqLeftJoyLeft = false;
            reqLeftJoyRight = false;
            reqLeftJoyMade = true;
            
//            Serial.print("LEFT Joystick Y Value: ");
//            Serial.println(String(reqLeftJoyYValue));
//            Serial.print("LEFT Joystick X Value: ");
//            Serial.println(String(reqLeftJoyXValue));

            if (reqLeftJoyYValue > 0) {
                reqLeftJoyDown = true;
            }

            if (reqLeftJoyYValue < 0) {
                reqLeftJoyUp = true;
            }

            if (reqLeftJoyXValue > 0) {
                reqLeftJoyRight = true;
            }
            
            if (reqLeftJoyXValue < 0) {
                reqLeftJoyLeft = true;
            }
     } else {
          if (reqLeftJoyMade) {
              reqLeftJoyUp = false;
              reqLeftJoyDown = false;
              reqLeftJoyLeft = false;
              reqLeftJoyRight = false;
              reqLeftJoyYValue = 0;
              reqLeftJoyXValue = 0;
              reqLeftJoyMade = false;
          }
     }

     if (PS5Request == "JR")
     {
            reqRightJoyUp = false;
            reqRightJoyDown = false;
            reqRightJoyLeft = false;
            reqRightJoyRight = false;
            reqRightJoyMade = true;
            
//            Serial.print("RIGHT Joystick Y Value: ");
//            Serial.println(String(reqRightJoyYValue));
//            Serial.print("RIGHT Joystick X Value: ");
//            Serial.println(String(reqRightJoyXValue));

            if (reqRightJoyYValue > 0) {
                reqRightJoyDown = true;
            }

            if (reqRightJoyYValue < 0) {
                reqRightJoyUp = true;
            }

            if (reqRightJoyXValue > 0) {
                reqRightJoyRight = true;
            }
            
            if (reqRightJoyXValue < 0) {
                reqRightJoyLeft = true;
            }
     } else {
          if (reqRightJoyMade) {
              reqRightJoyUp = false;
              reqRightJoyDown = false;
              reqRightJoyLeft = false;
              reqRightJoyRight = false;
              reqRightJoyYValue = 0;
              reqRightJoyXValue = 0;
              reqRightJoyMade = false;
          }
     }    
}

// Reset the PS5 request variables on every processing loop when needed
void resetRequestVariables()
{
    reqArrowUp = false;
    reqArrowDown = false;
    reqArrowLeft = false;
    reqArrowRight = false;
    reqCircle = false;
    reqCross = false;
    reqTriangle = false;
    reqSquare = false;
    reqL1 = false;
    reqL2 = false;
    reqR1 = false;
    reqR2 = false;
    reqShare = false;
    reqOptions = false;
    reqPS = false;
    reqJSLeftButton = false;
    reqJSRightButton = false;
}

void receivePS5Data(int bytes) {
  I2CInboundString = "";  // Clear the buffer   
  
  while (Wire.available()) {
    char c = Wire.read(); // Read a byte from the I2C bus
    if (c == '%') {   // '%' marks the end of the controller message
        I2CInboundString.trim();
        setPS5Request(I2CInboundString.substring(1,I2CInboundString.length()));  // Process the request leaving off first non-used I2C byte
        I2CInboundString = "";  // Clear the buffer    
    } else {
        I2CInboundString += c;  // Append the next character to the string buffer  
    }
  }
}

// Receive inbound serial messages from the Raspberry Pi
void check_inbound_serial_message() {
  static String message = ""; // Buffer to store incoming messages

  // Check if data is available on Serial3
  while (Serial3.available() > 0) {
    char incomingChar = Serial3.read(); // Read the incoming character

    // Check for the termination character '%'
    if (incomingChar == '%') {
      // Echo the message back to Serial Port
      Serial.println("Incoming Serial Message: " + message);

      // Set ControllerLive if this is the startup message from Raspberry Pi    
      if (message == "SysLive") {
          PS5ControllerLive = true;
          Serial.println("The Raspberry Pi is sending data");
          send_serial_message("SysLive");
      }

      // Based on the inbound message - SET YOUR STATE VARIABLES HERE
      if (message.length()>0){
//        Serial.println("Adruino recievd: " + message);
        commandRecieved = true;
        command = message;
      } else {
        commandRecieved = false;
      }

      // Clear the message buffer for the next message
      message = "";
    }

    // Add the character to the message buffer
    message += incomingChar;
    if (message == "%") {
      message = "";
    }
  }
}

// Send outbound serial messages to the Raspberry Pi - append termination byte '%' to message
void send_serial_message(String message) {
  message = message + "%";
  Serial3.println(message);
}
