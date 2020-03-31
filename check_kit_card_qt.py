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
 
import nfc
 
SYS_CODE = 0x93B1
SERVICE   = 64
BLOCK = 0
 
def play_sound( snd_obj ):
    snd_obj.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)
        
def NFC_detected(tag):
    idm, pmm = tag.polling(system_code=SYS_CODE)
    tag.idm, tag.pmm, tag.sys = idm, pmm, SYS_CODE
 
    sc = nfc.tag.tt3.ServiceCode( SERVICE, 0x0b)  
    bc = nfc.tag.tt3.BlockCode( BLOCK, service=0)
 
    data = tag.read_without_encryption([sc], [bc])
    txt=data.decode('utf-8').strip()
    play_sound(snd00)
    ui.l1_change(txt)
 
def NFC_Thread():
    time.sleep(2)
    while True:
        ui.l1_change('READY')
        try:
            with nfc.ContactlessFrontend('usb') as clf:
                clf.connect(rdwr={'on-connect': NFC_detected})
        except:
            pass
        time.sleep(.5)
        
    
class GUI(QWidget):
 
    def __init__(self, parent=None):
        
        super(GUI, self).__init__(parent)       
        self.resize(600,500)
        self.setWindowTitle('KIT-Card Reader')
        
        # 空の縦レイアウトを作る
        self.mylayout = QVBoxLayout()
        self.setLayout(self.mylayout)
        
        # ラベル
        self.l1 = QLabel('in progress... ')
        self.l1.setAlignment(Qt.AlignCenter)
        self.l1.setStyleSheet('color: black; font-size: 64pt')
        self.mylayout.addWidget(self.l1)
        xx=self.l1
 
        # ボタン
        self.b1 = QPushButton('終了',self)
        self.b1.setStyleSheet('background-color: maroon; color: white; font-size: 32pt')
        self.b1.clicked.connect(self.b1_callback)        
        self.mylayout.addWidget(self.b1)
 
    def b1_callback(self):
        print('...bye....')
        exit()
 
    def l1_change(self,txt):
        self.l1.setText(txt)
 
        
if __name__ == '__main__':
     
    # 効果音のロード
    pygame.mixer.init()
    snd00=pygame.mixer.Sound("in_time.wav")
    snd01=pygame.mixer.Sound("not_in_time.wav")
    
    # ウィンドウ準備
    app = QApplication(sys.argv)
    ui = GUI()
    ui.setWindowFlags(Qt.CustomizeWindowHint|Qt.WindowTitleHint)
    ui.show()
    
    # NFCカードリーダスレッド開始
    th_nfc=threading.Thread(target=NFC_Thread)    
    th_nfc.setDaemon(True) 
    th_nfc.start()
    
    # Windowイベント受付開始 
    sys.exit(app.exec_())
