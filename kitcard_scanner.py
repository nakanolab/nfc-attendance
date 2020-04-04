'''Provides GUI for NFC-based attendance.'''

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
 
import datetime
import logging
import sys
import threading
import time
import pygame.mixer
from qtpy.QtCore import Qt, QTimer
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QApplication, QComboBox, QLabel, QPushButton
from qtpy.QtWidgets import QVBoxLayout, QWidget
import nfc
import roster
 
SYS_CODE = 0x93B1
SERVICE = 64
BLOCK = 0
DELAY = 5  # 2以上を指定(5: 500ミリ秒でREADYに)

SUCCESS = True
FAILURE = False


class Buzzer:
    '''Plays two kinds of buzzer.'''
    def __init__(self):
        # 効果音のバッファサイズ変更（再生時のディレイを抑制）
        pygame.mixer.pre_init(22050, -16, 2, 512)
        pygame.mixer.init()
        # 効果音のロード
        self.sound = {SUCCESS: pygame.mixer.Sound('sound/in_time.wav'),
                      FAILURE: pygame.mixer.Sound('sound/not_in_time.wav')}

    def ring(self, status):
        if not pygame.mixer.get_busy():
            self.sound[status].play()


class GUI(QWidget):
    '''GUI for choosing course and monitoring scans of NFC ID cards.

    Attributes (other than Qt objects):
        roster: A Roster object.
        buzzer: A Buzzer object.
        last_student_id, blocked, wait: Used to avoid repeated GUI refreshes
            when an ID card is placed for prolonged period.
    '''
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)
        self.resize(600, 500)
        self.setWindowTitle('KIT-Card Reader')
        self.setFont(QFont('Helvetica', 24))
        
        # 名簿をロード
        self.roster = roster.Roster()

        # 空の縦レイアウトを作る
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # コンボボックス
        cbox_labels = [f'{course_code} {course_name}'
                       for course_code, course_name
                       in self.roster.courses.items()]
        self.cb1 = QComboBox(self)
        self.cb1.addItems(cbox_labels)
        layout.addWidget(self.cb1)
        
        # ラベル
        self.state = 'IDLE'
        self.l1 = QLabel(self.state)
        self.l1.setAlignment(Qt.AlignCenter)
        self.l1.setStyleSheet('color: black; font-size: 64pt')
        layout.addWidget(self.l1)
 
        # ボタン
        self.b1 = QPushButton('受付開始', self)
        self.b1.setStyleSheet('background-color: darkblue;'
                              'color: white; font-size: 32pt')
        self.b1.clicked.connect(self.b1_callback)
        layout.addWidget(self.b1)

        # ブザー
        self.buzzer = Buzzer()
 
        # タイマー(100ミリ秒ごとのインタバルタイマ)
        self.timer = QTimer()
        self.timer.setSingleShot(False)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.on_timer)
        self.wait = DELAY
        self.blocked = False
        self.last_student_id = None
        self.timer.start()
                   
    def b1_callback(self):
        '''Starts taking attendance.'''
        if self.state != 'IDLE':
            self.roster.report_absent_students()
            exit()
        self.state = 'RUNNING'
        idx = self.cb1.currentIndex()  # 現在のコンボボックスの選択番号
        self.cb1.setStyleSheet('background-color: gray;'
                               'color: white; font-size: 24pt')
        self.cb1.setEnabled(False)
        course_code = list(self.roster.courses)[idx]
        self.roster.set_course_code(course_code)

        # ボタンラベル変更
        self.update_button_label()
        self.b1.setStyleSheet('background-color: maroon;'
                              'color: white; font-size: 32pt')
        
        # NFCカードリーダスレッド開始
        t = threading.Thread(target=nfc_thread, args=(self,))
        t.daemon = True
        t.start()
 
    def l1_change(self, text):
        self.l1.setText(text)

    def update_button_label(self):
        num_students = len(self.roster.students)
        num_present = len(self.roster.present)
        self.b1.setText('受付終了 (%d/%d)' % (num_present, num_students))

    def check_in(self, student_id):
        '''Checks in a student.'''
        if self.last_student_id == student_id:
            return
        self.last_student_id = student_id
        ok, msg = self.roster.check_in(student_id)
        if ok:
            timestamp = datetime.datetime.now().strftime('%H:%M:%S')
            self.l1_change(f'{timestamp}\n{msg}')
            self.update_button_label()
            self.buzzer.ring(SUCCESS)
        else:
            self.l1_change(msg)
            self.buzzer.ring(FAILURE)

    def on_timer(self):
        if not self.blocked:
            self.blocked = True
            self.wait = DELAY
        elif self.wait > 0:
            self.wait -= 1
            if self.wait == 0:
                self.l1_change('READY')  # カードが見えないときはREADYに強制
                self.last_student_id = None


def get_student_id(tag):
    '''Extracts student ID from an NFC card.'''
    tag.polling(system_code=SYS_CODE)
    sc = nfc.tag.tt3.ServiceCode(SERVICE, 0x0b)
    bc = nfc.tag.tt3.BlockCode(BLOCK, service=0)
    data = tag.read_without_encryption([sc], [bc])
    return data.decode('utf-8').lstrip('0').rstrip()[:-2]

def nfc_thread(ui):
    def nfc_detected(tag):
        ui.check_in(get_student_id(tag))
    
    time.sleep(1)
    while True:
        while not ui.blocked:
            time.sleep(0.05)
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={'on-connect': nfc_detected})
        except Exception as e:
            logging.error(str(e))
            ui.buzzer.ring(FAILURE)
        ui.blocked = False


if __name__ == '__main__':
    # ウィンドウ準備
    app = QApplication(sys.argv)
    ui = GUI()
    ui.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
    ui.show()
    
    # Windowイベント受付開始
    sys.exit(app.exec_())
