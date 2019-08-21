from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, qApp
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtCore import QUrl, QDir, QFile, QIODevice, QTextStream, Qt
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist, QMediaMetaData
from playerwidget import PlayerWidget, PlayListWidget
from settings import settings
import playericon
import sys


class Window(QMainWindow):

    currentItem = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPlayer")
        self.setWindowIcon(QIcon(":/icon/music.svg"))
        self.setFixedWidth(420)
        self.setCentralWidget(QWidget(self))
        self.centralWidget().setLayout(QVBoxLayout())
        self.mainLayout = self.centralWidget().layout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.playerWidget = PlayerWidget(self)
        self.mainLayout.addWidget(self.playerWidget)

        self.playListWidget = PlayListWidget(self)
        self.mainLayout.addWidget(self.playListWidget)

        self.mediaPlayer = QMediaPlayer(self)
        self.mediaPlayer.setVolume(int(settings().value("volume") or 100))
        self.playList = QMediaPlaylist(self)
        self.mediaPlayer.setPlaylist(self.playList)

        self.playerWidget.playButtonClicked.connect(self.play)
        self.playerWidget.showOrHideClicked.connect(self.playListShowOrHide)
        self.playerWidget.volumeChanged.connect(self.volumeChange)
        self.playerWidget.mutedButtonClicked.connect(self.mutedChange)
        self.playerWidget.previousButtonClicked.connect(self.previousMusic)
        self.playerWidget.nextButtonClicked.connect(self.nextMusic)
        self.playerWidget.mixedButtonClicked.connect(self.shufflePlayList)
        self.playerWidget.repeatButtonClicked.connect(self.repeatPlayList)
        self.playerWidget.musicPositionMoved.connect(self.musicPositionMove)

        self.playListWidget.musicDrop.connect(self.addPlayList)
        self.playListWidget.itemDoubleClicked.connect(self.selectMusicPlay)

        self.mediaPlayer.audioAvailableChanged.connect(self.audioAvailableChanged)
        self.mediaPlayer.currentMediaChanged.connect(self.currentMediaChanged)
        # self.mediaPlayer.durationChanged.connect(self.durationChanged)
        # self.mediaPlayer.connect(SIGNAL("mediaChanged(QMediaContent *)"), self.mediaChanged)
        self.mediaPlayer.mutedChanged.connect(self.mutedChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.seekableChanged.connect(self.seekableChanged)
        self.mediaPlayer.stateChanged.connect(self.stateChanged)
        self.mediaPlayer.volumeChanged.connect(self.volumeChanged)
        self.mediaPlayer.error.connect(self.error)

        self.playList.loaded.connect(self.loaded)
        self.playList.loadFailed.connect(self.loadFailed)

        self.loadPlayList()
        self.mediaPlayer.playlist().setCurrentIndex(int(settings().value("currentMusic") or 0))

        item = self.playListWidget.item(int(settings().value("currentMusic") or 0))
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item
        playback = int(settings().value("playbackMode") or 2)
        if playback == 1:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        elif playback == 2:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.Sequential)
        elif playback == 3:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.Loop)

    def addPlayList(self, musics):
        self.playListWidget.addMusics(musics)
        for music in musics:
            self.playList.addMedia(QMediaContent(music))

    def selectMusicPlay(self, item):
        index = self.playListWidget.row(item)
        self.mediaPlayer.playlist().setCurrentIndex(index)
        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item
        self.mediaPlayer.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()

        elif self.mediaPlayer.state() == QMediaPlayer.PausedState:
            self.mediaPlayer.play()

        elif self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            if self.mediaPlayer.playlist().currentIndex() < 0:
                self.mediaPlayer.playlist().setCurrentIndex(0)

            self.mediaPlayer.setPosition(0)
            self.mediaPlayer.play()

    def playListShowOrHide(self):
        if self.playListWidget.isHidden():
            self.playListWidget.show()

        else:
            self.playListWidget.hide()


    def volumeChange(self, volume):
        self.mediaPlayer.setVolume(volume)

    def mutedChange(self):
        if self.mediaPlayer.isMuted():
            self.mediaPlayer.setMuted(False)

        else:
            self.mediaPlayer.setMuted(True)

    def previousMusic(self):
        self.mediaPlayer.playlist().previous()
        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item

    def nextMusic(self):
        self.mediaPlayer.playlist().next()
        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item

    def shufflePlayList(self):
        self.mediaPlayer.playlist().shuffle()
        self.playListWidget.clear()
        for media in range(self.mediaPlayer.playlist().mediaCount()):
            self.playListWidget.addMusic(self.mediaPlayer.playlist().media(media).canonicalUrl())

        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item

    def repeatPlayList(self):
        if self.mediaPlayer.playlist().playbackMode() == QMediaPlaylist.Sequential:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.Loop)
            self.playerWidget.repeatButtonStatus(3)

        elif self.mediaPlayer.playlist().playbackMode() == QMediaPlaylist.Loop:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            self.playerWidget.repeatButtonStatus(1)

        elif self.mediaPlayer.playlist().playbackMode() == QMediaPlaylist.CurrentItemInLoop:
            self.mediaPlayer.playlist().setPlaybackMode(QMediaPlaylist.Sequential)
            self.playerWidget.repeatButtonStatus(2)

    def musicPositionMove(self, pos):
        self.mediaPlayer.setPosition(pos)

    #mediaplayer signals
    def audioAvailableChanged(self, available):
        if "Duration" in self.mediaPlayer.availableMetaData():
            self.playerWidget.setDuration(self.mediaPlayer.metaData("Duration"))

        for data in self.mediaPlayer.availableMetaData():
            print(data, self.mediaPlayer.metaData(data))

    def currentMediaChanged(self, mediacontent):
        self.setWindowTitle(self.mediaPlayer.currentMedia().canonicalUrl().fileName())
        if self.currentItem:
            self.currentItem.setForeground(QBrush())
            self.currentItem.setBackground(QBrush())

        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        item.setForeground(Qt.lightGray)
        item.setBackground(Qt.darkGray)
        self.currentItem = item

    # def durationChanged(self, duration):
    #     pass

    # def mediaChanged(self, media):
    #     print(media)

    def mutedChanged(self, muted):
        if muted:
            self.playerWidget.mutedButtonStatus("muted")

        else:
            self.playerWidget.mutedButtonStatus("speaker")

    def positionChanged(self, pos):
        self.playerWidget.setPosition(pos)

    def seekableChanged(self, seekable):
        pass#print(seekable)

    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playerWidget.playButtonStatus("play")

        elif state == QMediaPlayer.PausedState:
            self.playerWidget.playButtonStatus("pause")

        elif state == QMediaPlayer.StoppedState:
            self.playerWidget.playButtonStatus("pause")

    def volumeChanged(self, volume):
        pass#print(volume)

    def error(self, err):
        print(err)

    def loaded(self):
        print("loaded")

    def loadFailed(self):
        print("loadFailed")

    def loadPlayList(self):
        file = QFile(QUrl.fromLocalFile(QDir.homePath()+"/.iplayer/playlist.db").toLocalFile())
        file.open(QIODevice.ReadOnly|QIODevice.Text)
        self.mediaPlayer.playlist().load(file, "m3u")

        file = QFile(QUrl.fromLocalFile(QDir.homePath() + "/.iplayer/playlist.db").toLocalFile())
        file.open(QIODevice.ReadOnly | QIODevice.Text)

        text = QTextStream(file)
        while not text.atEnd():
            line = text.readLine()
            if line.startswith("file:/"):
                self.playListWidget.addMusic(QUrl(line))

    def setWindowTitle(self, title):
        if not title.startswith("IPlayer"):
            super().setWindowTitle("IPlayer - " + title)

        else:
            super().setWindowTitle(title)

    def closeEvent(self, event):
        if not QDir().exists(QDir.homePath()+"/.iplayer"):
            QDir().mkdir(QDir.homePath()+"/.iplayer")
        self.mediaPlayer.playlist().save(QUrl.fromLocalFile(QDir.homePath()+"/.iplayer/playlist.db"), "m3u")

        settings().setValue("volume", self.mediaPlayer.volume())
        settings().setValue("currentMusic", self.mediaPlayer.playlist().currentIndex())
        settings().setValue("playbackMode", self.mediaPlayer.playlist().playbackMode())
        settings().sync()
        qApp.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())