'''
NOTE: Pygame
 python3 -m pip install -U pygame --user
 
 sudo apt-get install python3-qtpy
 
 qt5ct
   Style: gtk2 -> fusion
 
'''
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
 
import platform
import pygame.mixer
import sys
from qtpy.QtGui import *
from qtpy.QtCore import *
from qtpy.QtWidgets import *
import threading
import time
import roster as ros
import datetime
import nfc
 
SYS_CODE = 0x93B1
SERVICE   = 64
BLOCK = 0
RISYU_FILE ='risyu-2020.csv'

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

def NFC_detected(tag):
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
    student_class_no, student_name = registered_students[student_id]
    dt_now = datetime.datetime.now()
    dtstr=dt_now.strftime('%H:%M:%S\n')
    ui.l1_change(dtstr+student_class_no+'\n'+student_name) # Qtラベルの変更
        
def NFC_Thread():
    time.sleep(1)
    while True:
        ui.l1_change('READY') # Qtラベルの変更
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={'on-connect': NFC_detected})
        except Exception as e:
            print(e)
            print('(E_E) : timing error... ')
            play_result(False)
        try:
            time.sleep(1)
        except KeyboardInterrupt as e:
            print('writing to file...')
            return 
        time.sleep(.5)
    
class GUI(QWidget):
    stat='IDLE'
    def __init__(self, parent=None):
        
        super(GUI, self).__init__(parent)       
        self.resize(600,500)
        self.setWindowTitle('KIT-Card Reader')
        self.setFont(QFont("Helvetica", 24))
        
        # 空の縦レイアウトを作る
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        
        # コンボボックス
        self.cb1 = QComboBox(self)
        self.cb1.addItems(cbox_labels)
        self.cb1.activated[str].connect(self.activated)
        self.mylayout.addWidget(self.cb1)        
        
        # ラベル
        self.l1 = QLabel('IDLE')
        self.l1.setAlignment(Qt.AlignCenter)
        self.l1.setStyleSheet('color: black; font-size: 64pt')
        self.mylayout.addWidget(self.l1)
 
        # ボタン
        self.b1 = QPushButton('受付開始',self)
        self.b1.setStyleSheet('background-color: darkblue; color: white; font-size: 32pt')
        self.b1.clicked.connect(self.b1_callback)        
        self.mylayout.addWidget(self.b1)
 
    def activated(self, str0):
        idx=self.cb1.currentIndex() # 現在のコンボボックスの選択番号
        print("%d %s" % (idx,str0))
                   
    def b1_callback(self):
        global registered_students
        if self.stat !='IDLE':
                print('...bye....')
                exit()
        self.stat = 'RUNNING'
        self.b1.setText('受付終了')
        self.b1.setStyleSheet('background-color: maroon; color: white; font-size: 32pt')
        idx=self.cb1.currentIndex() # 現在のコンボボックスの選択番号
        self.cb1.setStyleSheet('background-color: gray; color: white; font-size: 24pt')
        self.cb1.setEnabled(False)
        course_code=list(courses.keys())[idx]
        registered_students = roster[course_code]
        print('========================================') 
        print(courses[course_code]);
        print('----------------------------------------') 
        for manage_num, student_id in enumerate(registered_students,1):
              student_class_no, student_name = registered_students[student_id]
              print(f'  {manage_num} {student_id} {student_class_no} {student_name}')
         # NFCカードリーダスレッド開始
        th_nfc=threading.Thread(target=NFC_Thread)    
        th_nfc.setDaemon(True) 
        th_nfc.start()
 
    def l1_change(self,txt):
        self.l1.setText(txt)
 
        
if __name__ == '__main__':
    courses, roster = ros.load_risyu(RISYU_FILE) 
    cbox_labels=[x+' '+y for (x,y) in courses.items()]
    present = set()
            
    # 効果音のロード
    pygame.mixer.init()
    snd00=pygame.mixer.Sound("in_time.wav")
    snd01=pygame.mixer.Sound("not_in_time.wav")
    
    # ウィンドウ準備
    app = QApplication(sys.argv)
    ui = GUI()
    ui.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowTitleHint)
    ui.show()
    
    # Windowイベント受付開始 
    sys.exit(app.exec_())