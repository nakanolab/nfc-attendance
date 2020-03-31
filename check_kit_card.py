'''
NOTE: Pygame

 python3 -m pip install -U pygame --user
'''

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame.mixer
import nfc
from binascii import hexlify
import time
import roster as ros

SYS_CODE = 0x93B1
SERVICE   = 64
BLOCK = 0
RISYU_FILE ='risyu-2020.csv'

# 効果音のロード
pygame.mixer.init()
snd00=pygame.mixer.Sound('in_time.wav')
snd01=pygame.mixer.Sound('not_in_time.wav')

def play_result(ok):
    if ok:
        play_sound(snd00)
    else:
        play_sound(snd01)
    
def play_sound( snd_obj ):
    snd_obj.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)

def get_student_id(data):
    return data.decode('utf-8').lstrip('0').rstrip()[:-2]

def on_connect(tag):
    idm, pmm = tag.polling(system_code=SYS_CODE)
    tag.idm, tag.pmm, tag.sys = idm, pmm, SYS_CODE
    sc = nfc.tag.tt3.ServiceCode( SERVICE, 0x0b)  
    bc = nfc.tag.tt3.BlockCode( BLOCK, service=0)
    data = tag.read_without_encryption([sc], [bc])
    student_id = get_student_id(data)
    # print(tag)
    # print('str:', data)
    # print('hex:', hexlify(data))
    ok = False
    if student_id not in registered_students:
        print('unregistered student: %s' % student_id)
    elif student_id in present:
        print('already checked in')
    else:
        print('adding student: %s' % student_id)
        present.add(student_id)
        ok = True
    play_result(ok)
    
def main():
    global registered_students
    print('========================================') 
    print('#','科目コード','科目名') 
    print('----------------------------------------') 
    for idx,(key,val) in enumerate(courses.items(),1):
        print(idx, key, val)
    print('----------------------------------------')
    while True:         
        idx=int(input('  科目番号を選択して下さい > '));
        if 1 <= idx <= len(courses):
            break
    course_code=list(courses.keys())[idx-1]
    registered_students = roster[course_code]
    print('========================================') 
    print(courses[course_code]);
    print('----------------------------------------') 
    for manage_num, student_id in enumerate(registered_students,1):
          student_class_no, student_name = registered_students[student_id]
          print(f'  {manage_num} {student_id} {student_class_no} {student_name}')
    print('========================================') 
    print('   カードをかざして下さい')
    print('----------------------------------------') 
    while True:
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={'on-connect': on_connect})
        except Exception as e:
            print(e)
            print('(E_E) : timing error... ')
            play_result(False)
        try:
            time.sleep(1)
        except KeyboardInterrupt as e:
            print('writing to file...')
            return

if __name__ == '__main__':
    courses, roster = ros.load_risyu(RISYU_FILE) 
    registered_students = None
    present = set()
    main()
