from PyQt5.QtWidgets import QDialog, QApplication,QPushButton,QLineEdit,QListWidget,QHBoxLayout,QVBoxLayout,\
    QListWidgetItem,QWidget,QLabel,QTextEdit
import sys
from PyQt5.QtCore import QSize,Qt
import requests
from bs4 import BeautifulSoup
import json
import os.path

cover_path=r'albumcover/'
music_path = r'music/'
class MusicBox(QDialog):
    def __init__(self):
        super(MusicBox, self).__init__()
        self.initUI()

    def initUI(self):
        self.resize(500, 400)
        self.setWindowTitle('获取音乐')
        source=QLabel('音乐来源：广软NA音乐网')
        self.search_box=QLineEdit()
        self.search_button=QPushButton('搜索')
        self.search_button.clicked.connect(self.search)
        self.search_result=QListWidget()
        title_label=QLabel('歌曲名')
        artist_label=QLabel('歌手')
        self.messages=QTextEdit()

        layout1=QHBoxLayout()
        layout1.addWidget(source)
        layout1.addWidget(self.search_box)
        layout1.addWidget(self.search_button)

        layout2=QHBoxLayout()
        layout2.addWidget(title_label)
        layout2.addWidget(artist_label)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout1)
        main_layout.addLayout(layout2)
        main_layout.addWidget(self.search_result,stretch=3)
        main_layout.addWidget(self.messages,stretch=1)

        self.setLayout(main_layout)
        self.show()

    def search(self):
        search_str=self.search_box.text()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'}
        url = 'http://music.seig.edu.cn/home/search-page?search-str=' + search_str
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, "html.parser")
            ls = soup.find_all("div", attrs={"class": "music-block"})
            self.search_result.clear()
            for div in ls:
                title = div.find('span', attrs={"class": "music-title"}).string
                artist = div.find('span', attrs={"class": "music-artist"}).string
                music_id = div.attrs['data-music-id']
                item = QListWidgetItem()
                item.setSizeHint(QSize(10, 40))
                music_item = ItemWidget(title, artist, music_id,self.messages)
                self.search_result.addItem(item)
                self.search_result.setItemWidget(item, music_item)
        except:
            self.messages.append('访问网页失败')
        else:
            self.messages.append('已搜索到%d个结果'%len(ls))


class ItemWidget(QWidget):
    def __init__(self,title,artist,music_id,messages):
        super(ItemWidget, self).__init__()
        self.title=title
        self.artist=artist
        self.music_id=music_id
        self.messages=messages

        title_label=QLabel(title)
        artist_label=QLabel(artist)
        artist_label.setAlignment(Qt.AlignCenter)
        download_button=QPushButton('下载')
        download_button.setFixedSize(50, 25)
        download_button.clicked.connect(self.download)
        layout=QHBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(artist_label)
        layout.addWidget(download_button)

        self.setLayout(layout)

    def download(self):
        url = 'http://music.seig.edu.cn/api/get-music/' + self.music_id
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'}
        self.messages.append('开始下载'+ self.title )
        try:
            response = requests.get(url=url, headers=headers)
            js = json.loads(response.text)

            url=js['data']['file_url']
            response = requests.get(url=url, headers=headers)

            if not os.path.exists(music_path):
                os.mkdir(music_path)
            filename = music_path+self.title+'-'+self.artist + '.mp3'
            f = open(filename, 'wb')
            f.write(response.content)
            f.close()

            cover_url = js['data']["album_cover_300_url"]
            response = requests.get(url=cover_url, headers=headers)
            if not os.path.exists(cover_path):
                os.mkdir(cover_path)
            filename = cover_path + self.title + '-' + self.artist + '.jpg'
            f = open(filename, 'wb')
            f.write(response.content)
            f.close()
        except:
            self.messages.append(self.title+'下载失败')
        else:
            self.messages.append(self.title+'下载成功')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MusicBox()
    sys.exit(app.exec_())

