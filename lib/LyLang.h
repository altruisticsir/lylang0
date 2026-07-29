/*
 * Welcome to the LyLang toolchain. If you're looking to add additional
 * functionality to the project, please take a look at the headers inside
 * of the "platforms" folder. Find your microcontroller of choice(or, if
 * it isn't available, add it!), and begin writing.
 */

#ifndef LYLANG
#define LYLANG

#ifdef __AVR_ATmega328P__
#include "platforms/atmega328p.h"
#else
#include "platforms/debug.h"
#endif

#define OFF 0
#define ON 1
#define TOGGLE 2

#define IN 0
#define OUT 1

#endif