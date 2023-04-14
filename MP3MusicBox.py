import sys
import pygame
from PyQt5.QtWidgets import QMainWindow, QApplication,QPushButton,QHBoxLayout,QWidget,\
    QSlider,QLabel,QListWidget,QVBoxLayout,QFileDialog,QCheckBox,QListWidgetItem
from PyQt5.QtGui import QIcon,QPixmap,QFont
from PyQt5.QtCore import QSize,QTimer,Qt
import os
import random
import time
from mutagen.mp3 import MP3
from downloadMP3 import MusicBox

music_path = r'music'
cover_path=r'albumcover/'
icon_path = r'icon/'
class MyPushButton(QPushButton):
    def __init__(self,icon_path,click_event):
        super().__init__()
        self.initUI(icon_path,click_event)

    def initUI(self,icon_path,click_event):
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(30, 30))
        self.setStyleSheet("border:none")
        self.clicked.connect(click_event)

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 600)
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress_refresh)
        self.play_mode = 'list_loop'  # 默认播放模式

        if not os.path.exists('playlist.txt'):
            f = open('playlist.txt', 'w+')
            ls = [music_path + '/' + music for music in os.listdir(music_path) if music.endswith('.mp3')]
            f.writelines('\n'.join(ls))
            f.close()
        f = open('playlist.txt', 'r')
        self.current_music_list = f.read().split('\n')
        for i in self.current_music_list:
            if i=='':
                self.current_music_list.remove(i)
        f.close()

        self.current_music=None
        self.music_index=0
        self.del_select_flag = False
        pygame.mixer.init()
        self.initUI()

    def initUI(self):
        global icon_path
        self.setWindowTitle('MP3音乐盒')
        self.setWindowIcon(QIcon(icon_path+'music.png'))
#left_vbox
        pixmap = QPixmap(cover_path + "no-cover.jpg")
        self.album_cover = QLabel()
        self.album_cover.setPixmap(pixmap)
        self.album_cover.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.current_music_lbl = QLabel('无播放音乐')
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.current_music_lbl.setFont(font)
        self.current_music_lbl.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        #   left_1_hbox
        self.music_progress = QSlider(Qt.Horizontal)
        self.music_progress.sliderReleased.connect(self.release_progress_sld)
        self.music_progress.sliderMoved.connect(self.timer.stop)  # 拖动滑条时停止定时器
        self.music_progress.setFixedSize(400, 20)
        self.cur_pos = QLabel('00:00')
        self.cur_pos.setFixedSize(50, 20)
        self.end_pos = QLabel('00:00')
        self.end_pos.setFixedSize(50, 20)
        #   left_1_hbox
        #   left_2_hbox
        self.mode_btn = MyPushButton(icon_path + 'retweet.png', self.change_mode)
        self.play_btn = MyPushButton(icon_path + 'media-play.png', self.click_play_btn)
        self.pre_btn = MyPushButton(icon_path + 'media-previous.png', self.play_pre_music)
        self.next_btn = MyPushButton(icon_path + 'media-next.png', self.play_next_music)
        self.volume_btn = MyPushButton(icon_path + 'volume-full.png', self.volume_off)
        self.volume_sld = QSlider(Qt.Horizontal)
        self.volume_sld.setFixedSize(100, 20)
        self.volume_sld.setValue(100)
        self.volume_sld.valueChanged.connect(self.change_volume)
        #   left_2_hbox
 # left_vbox
# right_vbox
        #  right_1_hbox
        self.music_list_lbl = QLabel('播放列表')
        self.plus_btn = MyPushButton(icon_path + 'plus.png', self.add_music)
        self.plus_btn.setIconSize(QSize(20, 20))
        self.download_btn = MyPushButton(icon_path + 'cloud-download.png', self.show_download_dialog)
        self.download_btn.setIconSize(QSize(20, 20))
        self.refresh_btn = MyPushButton(icon_path + 'clockwise.png', self.refresh_music_list)
        self.refresh_btn.setIconSize(QSize(20, 20))
        self.del_btn = MyPushButton(icon_path + 'trash.png', self.del_music)
        self.del_btn.setIconSize(QSize(20, 20))
        self.select_all = QCheckBox('全选')
        self.select_all.stateChanged.connect(self.on_select_all)
        #  right_1_hbox
        self.music_list = QListWidget()
        self.music_list.addItems(self.current_music_list)
        self.music_list.itemDoubleClicked.connect(self.dbclick_item)
#   right_vbox
        left_vbox=QVBoxLayout()
        left_1_hbox= QHBoxLayout()
        left_1_hbox.addWidget(self.cur_pos)
        left_1_hbox.addWidget(self.music_progress)
        left_1_hbox.addWidget(self.end_pos)
        left_2_hbox=QHBoxLayout()
        left_2_hbox.addWidget(self.mode_btn)
        left_2_hbox.addWidget(self.pre_btn)
        left_2_hbox.addWidget(self.play_btn)
        left_2_hbox.addWidget(self.next_btn)
        left_2_hbox.addWidget(self.volume_btn)
        left_2_hbox.addWidget(self.volume_sld)
        left_vbox.addWidget(self.album_cover,stretch=5)
        left_vbox.addWidget(self.current_music_lbl,stretch=1)
        left_vbox.addLayout(left_1_hbox)
        left_vbox.addLayout(left_2_hbox)

        right_vbox=QVBoxLayout()
        self.right_1_hbox=QHBoxLayout()
        self.right_1_hbox.addWidget(self.music_list_lbl)
        self.right_1_hbox.addWidget(self.plus_btn)
        self.right_1_hbox.addWidget(self.download_btn)
        self.right_1_hbox.addWidget(self.refresh_btn)
        self.right_1_hbox.addWidget(self.del_btn)
        right_vbox.addLayout(self.right_1_hbox)
        right_vbox.addWidget(self.music_list)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_vbox,stretch=2)
        main_layout.addLayout(right_vbox,stretch=1)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)
        self.show()

    def click_play_btn(self):
        global icon_path
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.play_btn.setIcon(QIcon(icon_path + 'media-play.png'))
        elif self.current_music:
            pygame.mixer.music.unpause()
            self.play_btn.setIcon(QIcon(icon_path + 'media-pause.png'))
        elif len(self.current_music_list):
            self.play()

    def play_next_music(self):
        if self.play_mode=='list_loop':
            self.music_index += 1
        elif self.play_mode=='single_loop':
            pass
        elif self.play_mode=='shuffle':
            self.music_index = random.randint(0,len(self.current_music_list))
        self.play()

    def play_pre_music(self):
        if self.play_mode == 'list_loop':
            self.music_index -= 1
        elif self.play_mode == 'single_loop':
            pass
        elif self.play_mode == 'shuffle':
            self.music_index = random.randint(0, len(self.current_music_list))
        self.play()

    def play(self):
        if len(self.current_music_list):
            self.progress_value = 0
            self.current_music = self.current_music_list[(self.music_index) % len(self.current_music_list)]
            self.current_music_lbl.setText(self.current_music)
            album_cover_img=cover_path + self.current_music.split('/')[-1].split('.')[0] + '.jpg'
            if os.path.exists(album_cover_img):
                self.album_cover.setPixmap(QPixmap(album_cover_img))
            else:
                self.album_cover.setPixmap(QPixmap(cover_path +"no-cover.jpg"))
            pygame.mixer.music.load(self.current_music)
            pygame.mixer.music.play()
            self.play_btn.setIcon(QIcon(icon_path + 'media-pause.png'))
            self.timer.start(1000)
        else:
            self.current_music =None
            self.current_music_lbl.setText('无播放音乐')

    def change_mode(self):
        if self.play_mode=='list_loop':
            self.mode_btn.setIcon(QIcon(icon_path+'media-loop.png'))
            self.play_mode='single_loop'
        elif self.play_mode=='single_loop':
            self.mode_btn.setIcon(QIcon(icon_path + 'media-shuffle.png'))
            self.play_mode = 'shuffle'
        elif self.play_mode=='shuffle':
            self.mode_btn.setIcon(QIcon(icon_path + 'retweet.png'))
            self.play_mode = 'list_loop'

    def progress_refresh(self):
        if pygame.mixer.music.get_busy():
            music_length=MP3(self.current_music).info.length
            self.music_progress.setRange(0, int(music_length))
            self.timer.start(1000)
            self.music_progress.setValue(pygame.mixer.music.get_pos()//1000+self.progress_value)
            self.cur_pos.setText(time.strftime('%M:%S',time.localtime(pygame.mixer.music.get_pos()//1000+self.progress_value)))
            self.end_pos.setText(time.strftime('%M:%S',time.localtime(music_length)))
            if self.cur_pos.text()==self.end_pos.text():
                self.play_next_music()

    def release_progress_sld(self):
        if self.current_music:
            self.progress_value = self.music_progress.value()
            pygame.mixer.music.stop()
            pygame.mixer.music.play(0,self.music_progress.value())
            self.timer.start(1000)

    def dbclick_item(self):
        self.music_index=self.music_list.currentRow()
        self.play()

    def volume_off(self):
        if pygame.mixer.music.get_volume()>0:
            pygame.mixer.music.set_volume(0)
            self.volume_btn.setIcon(QIcon(icon_path+'volume-off.png'))
        else:
            pygame.mixer.music.set_volume(self.volume_sld.value()/100)
            self.volume_btn.setIcon(QIcon(icon_path + 'volume-full.png'))

    def change_volume(self):
        pygame.mixer.music.set_volume(self.volume_sld.value()/100)
        if pygame.mixer.music.get_volume():
            self.volume_btn.setIcon(QIcon(icon_path + 'volume-full.png'))
        else:
            self.volume_btn.setIcon(QIcon(icon_path + 'volume-off.png'))

    def add_music(self):
        fname = QFileDialog.getOpenFileNames(self, '获取本地mp3文件', 'C:/',"mp3文件(*.mp3)")
        if fname:
            self.current_music_list.extend(fname[0])
            f = open('playlist.txt', 'w')
            f.writelines('\n'.join(self.current_music_list))
            f.close()
            self.music_list.addItems(fname[0])

    def del_music(self):
        if self.del_select_flag:
            for i in range(self.music_list.count()):
                cb=self.music_list.itemWidget(self.music_list.item(i))
                if cb.isChecked():
                    if self.current_music==cb.text():
                        pygame.mixer.music.unload()
                        self.music_index=0
                    if os.path.dirname(cb.text())==music_path:
                        os.remove(cb.text())
                    album_cover_img = cover_path + cb.text().split('/')[-1].split('.')[0] + '.jpg'
                    if os.path.exists(album_cover_img):
                        os.remove(album_cover_img)
                    self.current_music_list.remove(cb.text())
            self.play()
            self.music_list.clear()
            self.music_list.addItems(self.current_music_list)
            f = open('playlist.txt', 'w')
            f.writelines('\n'.join(self.current_music_list))
            f.close()
            self.select_all.setVisible(0)
            self.right_1_hbox.replaceWidget(self.select_all,self.music_list_lbl)
            self.music_list_lbl.setVisible(1)
            self.del_select_flag = False
        else:
            self.music_list_lbl.setVisible(0)
            self.right_1_hbox.replaceWidget(self.music_list_lbl,self.select_all)
            self.select_all.setVisible(1)
            self.del_select_flag=True
            self.music_list.clear()
            self.boxes = set()
            for music_name in self.current_music_list:
                box = QCheckBox(music_name)
                box.stateChanged.connect(self.on_state_changed)
                self.boxes.add(box)
                item = QListWidgetItem(self.music_list)
                self.music_list.setItemWidget(item, box)

    def on_select_all(self, state):
        if state != 1:
            for ch in self.boxes:
                ch.setCheckState(state)

    def on_state_changed(self):
        checked_count=len([ch for ch in self.boxes if ch.checkState()])
        if checked_count == self.music_list.count():
            self.select_all.setCheckState(2)
        elif checked_count:
            self.select_all.setCheckState(1)
        else:
            self.select_all.setCheckState(0)

    def refresh_music_list(self):
        for music in os.listdir(music_path):
            music=music_path + '/'+music
            if music not in self.current_music_list:
                self.current_music_list.append(music)
        f = open('playlist.txt', 'w')
        f.writelines('\n'.join(self.current_music_list))
        f.close()
        self.music_list.clear()
        self.music_list.addItems(self.current_music_list)

    def show_download_dialog(self):
        self.download_dialog= MusicBox()
        self.download_dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mplayer = MusicPlayer()
    sys.exit(app.exec_())
