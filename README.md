# pymorse

*The original code is from Oz Nahum Tiram. URL https://oz123.github.io/writings/morse-fun-with-python*

**Modified by Bhaskar Tallamraju**

 ### Changes 06/20
  + modified the code to make it work with Python 3. Tested it with python 3.8 on Ubuntu 20.04
  + added morse test code
    + random alpha numeric morse code generation
    + random morse code for most common 500 english words

 ## REQUIREMENTS:  
       1. pyalsaaudio
       2. wave 

 ## Most common usage:
       1. ./pymorse.py -o sound "Hello World"                   # play the morse code for Hello World
       2. ./pymorse.py -o sound -r alphanum -c 20               # this is to test your translation skill for receiving alphabets and numerals
       3. ./pymorse.py -o sound -r word -c 52                   # this is to test your translation skill for receiving random words (from 500 common english word)
       4. ./pymorse.py -o text "Hello"                          # Outputs morse code to stdout
       5. ./pymorse.py -o text ".- / -. . .-- / -.-. --- -.. ." # Outputs the translated text 
