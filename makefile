SHELL := cmd.exe

true := .
path := main

make:
	python src/main.py
	avr-gcc -Wall -Os -lfto -mmcu=atmega328p -c $(path).cpp -o $(path).o
	avr-gcc -mmcu=atmega328p $(path).o -o $(path).elf
	avr-objcopy -O ihex -R .eeprom $(path).elf $(path).hex
	avrdude -c usbasp -p m328p -U flash:w:$(path).hex:i
	-del /q $(true)\*.elf $(true)\*.hex $(true)\*.pdb $(true)\*.o