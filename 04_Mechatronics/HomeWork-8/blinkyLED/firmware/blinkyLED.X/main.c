/* 
 * File:   main.c
 * Author: Vismaya Walawalkar
 *
 * Created on April 11, 2017, 11:08 AM
 */

#include <stdio.h>
#include <stdlib.h>

#include <xc.h>           // processor SFR definitions
#include <sys/attribs.h>  // __ISR macro

#include"blinky.h"
#include"i2c.h"
#include"ILI9163C.h"
// PIC32MX250F128B Configuration Bit Settings

// 'C' source line config statements
// DEVCFG0
#pragma config DEBUG = 0b11 // no debugging
#pragma config JTAGEN = OFF // no jtag
#pragma config ICESEL = ICS_PGx1 // use PGED1 and PGEC1
#pragma config PWP = OFF // no write protect
#pragma config BWP = OFF // no boot write protect
#pragma config CP = OFF // no code protect

// DEVCFG1
#pragma config FNOSC = PRIPLL // use primary oscillator with pll
#pragma config FSOSCEN = OFF // turn off secondary oscillator
#pragma config IESO = OFF // no switching clocks
#pragma config POSCMOD = HS // high speed crystal mode
#pragma config OSCIOFNC = OFF // disable secondary osc
#pragma config FPBDIV = DIV_1 // divide sysclk freq by 1 for peripheral bus clock
#pragma config FCKSM = CSDCMD // do not enable clock switch
#pragma config WDTPS = PS1048576 // use slowest wdt
#pragma config WINDIS = OFF // wdt no window mode
#pragma config FWDTEN = OFF // wdt disabled
#pragma config FWDTWINSZ = WINSZ_25 // wdt window at 25%

// DEVCFG2 - get the sysclk clock to 48MHz from the 8MHz crystal
//#pragma config FPLLIDIV = DIV_2 // divide input clock to be in range 4-5MHz
//#pragma config FPLLMUL = MUL_24 // multiply clock after FPLLIDIV
#pragma config FPLLODIV = DIV_2 // divide clock after FPLLMUL to get 48MHz


// DEVCFG3
#pragma config USERID = 2017 // some 16bit userid, doesn't matter what
//#pragma config PMDL1WAY = OFF // allow multiple reconfigurations
//#pragma config IOL1WAY = OFF // allow multiple reconfigurations

// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

#define MASKSIGN 0b0111111111111111

float get_data(unsigned short, unsigned short, short, short );

float get_data(unsigned short regH, unsigned short regL, short offset, short multiplier ){
    return( (float)((multiplier * ( ((regH<<8)|regL) & MASKSIGN )/65535) - offset) );
}
int main() {
   __builtin_disable_interrupts();

    // set the CP0 CONFIG register to indicate that kseg0 is cacheable (0x3)
    __builtin_mtc0(_CP0_CONFIG, _CP0_CONFIG_SELECT, 0xa4210583);
    
    // 0 data RAM access wait states
    BMXCONbits.BMXWSDRM = 0x0;
    // enable multi vector interrupts
    INTCONbits.MVEC = 0x1;
    // disable JTAG to get pins back
    DDPCONbits.JTAGEN = 0; 
    
    ANSELBbits.ANSB2 = 0;
    ANSELBbits.ANSB3 = 0;
    
    //i2c_master_setup();
    //i2c_write(MCP23008,0x05,0b00100000);
    //Initialize the blinky
    init_blinky();
    
    // Initialize the SPI module
    SPI1_init();
   
    //Initialize LCD interface
    LCD_init();
    
    //Init I2C
    i2c_master_setup();
    

    // Set background color
    LCD_clearScreen(BLACK);
    __builtin_enable_interrupts();
    /*Write string of arbitary characters*/
    unsigned short x0 = 28;
    unsigned short y0 = 32;
    int dd,len0;
    unsigned short total_time, ij;
    
    for(dd = 0; dd<1000000; dd++);
    LCD_writechar(15, 20, "IMU - aX aY");
    //LCD_writechar(45, 32, "Bars of Acceleration in X and Y");
    //LCD_writechar(10, 32, "GYRO");
    //LCD_writechar(80, 32, "ACCL");
    
    unsigned char data1;
    unsigned char IMU_data[14];
    char snum[10];
    
    float temp_data, gyroX, gyroY, gyroZ, accX, accY, accZ;
            
    data1 = i2c_read(MCP23008, WHOAMI);
    //Test is device responds
    LCD_writeint(1, 1, data1);
    
    //Initialize the IMU
    i2c_write(MCP23008,CTRL1_XL, 0b10000000); ///1000 for 1.66 kHz sample rate, 00 for 2g sensitivity, 00 for 400kHz baud
    i2c_write(MCP23008,CTRL2_G,0b10000000); //1000 for 1.66 kHz, 00 for 245 dps sensitivity, 
    i2c_write(MCP23008,CTRL3_C,0b00000100); //IF_INC bit 1 will enable the ability to read multiple registers
    
    while(1) {
        
        x0 = 28;
        y0 = 32 + 15;
        len0 = 10;
        ij = 0;
        
        i2c_master_multiread(MCP23008,0x20,14,IMU_data);
        
        temp_data = get_data(IMU_data[1], IMU_data[0], -40, 85 );
        LCD_writechar(35,1, "Temp, F =  ");
        LCD_writeint(105, 1, temp_data);
        // convert 123 to string [buf]
        
        gyroX = get_data(IMU_data[3], IMU_data[2], 0, 360 );
        //LCD_writeint(10, 60, gyroX);
        
        gyroY = get_data(IMU_data[5], IMU_data[4], 0, 360 );
        //LCD_writeint(10, 80, gyroY);
        
        gyroZ = get_data(IMU_data[7], IMU_data[6], 0, 360 );
        //LCD_writeint(10, 100, gyroZ);
        
        accX = get_data(IMU_data[9], IMU_data[8], 0, 980 );
        LCD_writeint(10, 100, accX);
        LCD_drawBar(64, 64, 100, 0, BLACK);
        LCD_drawBar(64, 64, 10 + ((accX+1)/9.8), 0, CYAN);
        
        accY = get_data(IMU_data[11], IMU_data[10], 0, 980 );
        LCD_writeint(80, 100, accY);
        LCD_drawBar(64, 64, 100, 1, BLACK);
        LCD_drawBar(64, 64, 10 + ((accY+1)/9.8), 1, MAGENTA);
        
        accZ = get_data(IMU_data[13], IMU_data[12], 0, 980 );
        //LCD_writeint(80, 100, accZ);
        
        for(dd = 0; dd<1000000; dd++);
    }  
}