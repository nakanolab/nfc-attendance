import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import platform
import pygame.mixer
import time

def sound_test(fname):
    snd=pygame.mixer.Sound(fname)
    snd.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)

if platform.system() == 'Linux':
    os.system('sox -b 16 -D -G -n -c 1 in_time.wav synth .04 pluck 880')
    os.system('sox -b 16 -D -G -n -c 1 not_in_time.wav synth .02 pluck 220 delay .1 repeat 1')
    
    pygame.mixer.init()
    sound_test('in_time.wav')
    sound_test('not_in_time.wav')
print('...bye')



