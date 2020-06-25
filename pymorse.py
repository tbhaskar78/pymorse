#!/usr/bin/env python
'''
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at https://mozilla.org/MPL/2.0/.


 The original code is from Oz Nahum Tiram. URL https://oz123.github.io/writings/morse-fun-with-python
 Modified by Bhaskar Tallamraju 

 Changes 06/20
  + modified the code to make it work with Python 3. Tested it with python 3.8 on Ubuntu 20.04
  + added morse test code
    + random alpha numeric morse code generation
    + random morse code for most common 500 english words

 REQUIREMENTS: 
       1. pyalsaaudio
       2. wave 

 Most common usage:
       1. ./pymorse.py -o sound "Hello World"                   # play the morse code for Hello World
       2. ./pymorse.py -o sound -r alphanum -c 20               # this is to test your translation skill
       3. ./pymorse.py -o sound -r word -c 52                   # this is to test your translation skill
       4. ./pymorse.py -o text "Hello"                          # Outputs morse code to stdout
       5. ./pymorse.py -o text ".- / -. . .-- / -.-. --- -.. ." # Outputs the translated text 

'''
import argparse
import wave
import math
import re
import struct
import sys
import tempfile
import string
import random
import time
import signal

from os import system
from morsedict import english_common_500
from morsedict import morse_dict

reverse_morse_dict = {v:k for k,v in list(morse_dict.items())}

def write_signal(wavef, duration, volume=0, rate=44100.0,
                 frequency=1240.0):
        '''
        rate = 44100.0       # Sample rate in Hertz
        duration = 0.1       # seconds
        frequency = 1240.0   # hertz
        '''
        for i in range(int(duration * rate * duration)):
                # max volume 32767.0
                value = int(volume*math.sin(frequency*math.pi*float(i)/float(rate)))
                data = struct.pack(B'<h', value)
                wavef.writeframesraw(data)


def text_to_morse(text, separator=";"):
        """translate a string to morse code in dot dash form"""
        morse = []
        for word in text.split():
                morse_word = []
                for w in word:
                        morse_word.append(morse_dict[w])
                morse.append(' '.join(morse_word))

        return separator.join(morse)


def morse_to_wav(text, file_=None):
    # TODO: figure out how to calibrate this for 5 wpm, 10 wpm, 20 wpm etc.
    # need to try to standardize it with a word like PARIS
    five_wpm  = {'.': 0.3, '-': 0.6, ';': 0.6, ' ': 0.9}
    char2signal = five_wpm

    if not file_:
        _, file_ = tempfile.mkstemp(".wav")

    wav = wave.open(file_, 'wb')
    wav.setnchannels(1) # mono
    wav.setsampwidth(2)
    rate = 44100.0
    wav.setframerate(rate)

    for char in text:
        if char == ';':
            write_signal(wav, char2signal[char], volume=0)
        elif char == ' ':
            write_signal(wav, char2signal[char], volume=0)
        else:
            write_signal(wav, char2signal[char], volume=32767.0)
            write_signal(wav, 0.4, volume=0)

    wav.writeframes(B'')
    wav.close()

    return file_


def play(f, device='default'):
    try:
        import alsaaudio
    except ImportError:
        print("You need to install pyalsaaudio")

    device = alsaaudio.PCM(device=device)

    # Set attributes
    f = wave.open(f, 'rb')
    device.setchannels(f.getnchannels())
    device.setrate(f.getframerate())

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif f.getsampwidth() == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_LE)
    elif f.getsampwidth() == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')

    device.setperiodsize(320)

    data = f.readframes(320)
    while data:
        # Read data from stdin
        device.write(data)
        data = f.readframes(320)


def morse_to_text(text, separator=" / "):
    """translate dash dot morse code to ascii text"""
    translated = []
    words = text.split(separator)
    for word in words:
            clear = []
            chars = word.split()
            for c in chars:
                    clear.append(reverse_morse_dict[c])
            translated.append(''.join(clear))

    return ' '.join(translated)


def signal_handler(sig, frame):
    print('Exiting ... ')
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    if sys.version_info[0] < 3:
        raise Exception("Python 3 or a more recent version is required.")

    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='a simple morse generator, translator and tester',
        formatter_class=argparse.HelpFormatter)

    parser.add_argument("-o", help="Specify the output format: text or sound",
                        choices=['text', 'sound'])
    parser.add_argument('-f', help="Specify the name of the wav file to write", action='store',
                            type=str)
    parser.add_argument('-r', help="TEST YOUR SKILL - randomly play morse for alphanumeric or the"
                        "most common 500 english words for testing", choices=['alphanum', 'word'])
    parser.add_argument('-c', help="how many times to test, default is 10",
                        action='store', type=int, default=1)
    parser.add_argument('args', nargs=argparse.REMAINDER)

    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit()
    
    if args.o == 'sound':
        # Testing code 
        if args.r:
            for i in range(args.c):
                system('clear')
                print ("READY...playing the code in 2 secs ")
                time.sleep(2)
                if args.r == 'alphanum':
                    random_num = random.randint(100, 999)
                    if random_num < 499: 
                        random_letter = random.choice(string.ascii_letters)
                    else:
                        random_letter = str(random.randint(0, 9))
                elif args.r == 'word':
                    random_letter = random.choice(english_common_500)

                morse = text_to_morse(random_letter)
                f = morse_to_wav(morse, file_=args.f)
                check = 'y'
                trycount = 0
                while check == 'y':
                    trycount = trycount + 1
                    if not args.f:
                        play(f)
                    char = input("enter your guess : ")
                    if char == random_letter.lower():
                        print("You got it!!!")
                        break
                    else:
                        if trycount == 3:
                            print("Max chances used. The letter is ", random_letter.lower())
                            check = 'n'
                            break
                        check = input("OOPS... wanna try again (y|n) ? ")
                        if check == 'n':
                            break
                        else:
                            check = 'y'
                        print ("playing the same code again in 2 secs ... ")
                        time.sleep(2)

                enter = input("Press ENTER")
        else:    
            morse = text_to_morse(' '.join(args.args))
            f = morse_to_wav(morse, file_=args.f)
            if not args.f:
                play(f)
    else:
        text = ' '.join(args.args)
        if re.search("[a-z0-9]+", text.lower()):
            conv = text_to_morse(text)
        else:
            conv = morse_to_text(text)
        if not args.f:
            sys.stdout.write(''.join(conv))
            sys.stdout.write('\n')
            sys.stdout.flush()
        else:
            f = open(args.f, 'w')
            f.write(morse+'\n')


# end of file
