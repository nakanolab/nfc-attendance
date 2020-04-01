import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
 
import datetime
import threading
import time
import sys
import pygame.mixer
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QApplication, QComboBox, QLabel, QPushButton
from qtpy.QtWidgets import QVBoxLayout, QWidget
import nfc
import roster
 
SYS_CODE = 0x93B1
SERVICE = 64
BLOCK = 0

SUCCESS = True
FAILURE = False


class Buzzer:
    def __init__(self):
        # 効果音のロード
        pygame.mixer.init()
        self.sound = {SUCCESS: pygame.mixer.Sound('sound/in_time.wav'),
                      FAILURE: pygame.mixer.Sound('sound/not_in_time.wav')}

    def ring(self, status):
        self.sound[status].play()
        while pygame.mixer.get_busy():
            time.sleep(0.1)


class GUI(QWidget):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)       
        self.resize(600, 500)
        self.setWindowTitle('KIT-Card Reader')
        self.setFont(QFont('Helvetica', 24))
        
        # 名簿をロード
        self.roster = roster.Roster()

        # 空の縦レイアウトを作る
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        
        # コンボボックス
        cbox_labels = [f'{course_code} {course_name}'
                       for course_code, course_name
                       in self.roster.courses.items()]
        self.cb1 = QComboBox(self)
        self.cb1.addItems(cbox_labels)
        self.cb1.activated[str].connect(self.activated)
        self.mylayout.addWidget(self.cb1)        
        
        # ラベル
        self.stat = 'IDLE'
        self.l1 = QLabel(self.stat)
        self.l1.setAlignment(Qt.AlignCenter)
        self.l1.setStyleSheet('color: black; font-size: 64pt')
        self.mylayout.addWidget(self.l1)
 
        # ボタン
        self.b1 = QPushButton('受付開始',self)
        self.b1.setStyleSheet('background-color: darkblue;'
                              'color: white; font-size: 32pt')
        self.b1.clicked.connect(self.b1_callback)        
        self.mylayout.addWidget(self.b1)

        # ブザー
        self.buzzer = Buzzer()
 
    def activated(self, text):
        idx = self.cb1.currentIndex()  # 現在のコンボボックスの選択番号
        print("%d %s" % (idx, text))
                   
    def b1_callback(self):
        if self.stat != 'IDLE':
            print('...bye....')
            exit()
        self.stat = 'RUNNING'
        idx = self.cb1.currentIndex()  # 現在のコンボボックスの選択番号
        self.cb1.setStyleSheet('background-color: gray;'
                               'color: white; font-size: 24pt')
        self.cb1.setEnabled(False)
        course_code = list(self.roster.courses.keys())[idx]
        self.roster.set_course_code(course_code)
        print('========================================') 
        print(self.roster.courses[course_code])
        print('----------------------------------------') 
        for i, student_id in enumerate(self.roster.students, 1):
              student_class_no, student_name = self.roster.students[student_id]
              print(f'  {i} {student_id} {student_class_no} {student_name}')
        # ボタンラベル変更
        num_students = len(self.roster.students)
        self.b1.setText('受付終了 (%d/%d)' % (0, num_students))
        self.b1.setStyleSheet('background-color: maroon;'
                              'color: white; font-size: 32pt')
        
        # NFCカードリーダスレッド開始
        th_nfc = threading.Thread(target=nfc_thread)
        th_nfc.setDaemon(True) 
        th_nfc.start()
 
    def l1_change(self, text):
        self.l1.setText(text)

    def check_in(self, student_id):
        ok, msg = self.roster.check_in(student_id)
        if ok:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            self.l1_change(f'{timestamp}\n{msg}')
            num_students = len(self.roster.students)
            num_present = len(self.roster.present)
            self.b1.setText('受付終了 (%d/%d)' % (num_present, num_students))
            self.buzzer.ring(SUCCESS)
        else:
            self.l1_change(msg)
            self.buzzer.ring(FAILURE)


def get_student_id(tag):
    idm, pmm = tag.polling(system_code=SYS_CODE)
    tag.idm, tag.pmm, tag.sys = idm, pmm, SYS_CODE
    sc = nfc.tag.tt3.ServiceCode(SERVICE, 0x0b)
    bc = nfc.tag.tt3.BlockCode(BLOCK, service=0)
    data = tag.read_without_encryption([sc], [bc])
    return data.decode('utf-8').lstrip('0').rstrip()[:-2]

def nfc_detected(tag):
    student_id = get_student_id(tag)
    ui.check_in(student_id)
    
def nfc_thread():
    time.sleep(1)
    while True:
        ui.l1_change('READY')  # Qtラベルの変更
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={'on-connect': nfc_detected})
        except Exception as e:
            print(str(e))
            ui.buzzer.ring(FAILURE)
        time.sleep(1)


if __name__ == '__main__':
    # ウィンドウ準備
    app = QApplication(sys.argv)
    ui = GUI()
    ui.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowTitleHint)
    ui.show()
    
    # Windowイベント受付開始 
    sys.exit(app.exec_())
