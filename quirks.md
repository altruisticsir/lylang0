## Known Quirks
You should put these quirks into consideration. If you write idiomatically, then these issues will mostly be avoided.

1. If you omit return 0 in proc main, the program will automatically add it for you. This, however, also adds return 0 to ALL procs with the same body content as main. While unlikely for any other proc to contain the same code as proc main, it is not impossible and should be considered

2. The type that a proc inherits comes from the FIRST token of the return statement. So, if you write return 10 + 10.0, you won't get a float proc, but rather an int proc because the first token is an integer. While easily avoidable by placing mathematical operations outside of return statements, it can still be an issue for those who write in non-idiomatic ways
(This problem has been addressed; 10 + 10.0 DOES result in a float proc and vice versa)

3. Indentation is not automatically applied. This isn't an issue, because C/C++ does not rely on indentation, but makes the result generally harder to read

4. When assigning the return value of a class method, you cannot perform any math operation on that returned value in the same variable assignment; you need to separate them. For example, you cannot do "make x = eeprom.read(2) + 10". You need to write "make x = eeprom.read(2)" and then "x += 10" instead