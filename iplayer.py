from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, qApp, QListWidgetItem
from PyQt5.QtWinExtras import QWinTaskbarButton, QWinThumbnailToolBar, QWinThumbnailToolButton
from PyQt5.QtGui import QBrush, QIcon
from PyQt5.QtCore import QUrl, QDir, QFile, QIODevice, QTextStream, Qt, QThread, pyqtSignal
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from playerwidget import PlayerWidget, PlayListWidget
from settings import settings
import playericon
import sys
from pynput.keyboard import Key, Listener


class CaptureKey(QThread):

    captureKeyState = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()

    def listen(self):
        with Listener(
                on_press=self.on_press) as self.listener:
            self.listener.join()


    def on_press(self, key):
        key = str(key)
        if key == "<177>":
            self.captureKeyState.emit("prev")

        elif key == "<179>": #play and pause
            self.captureKeyState.emit("play")

        elif key == "<176>": #next
            self.captureKeyState.emit("next")

    def run(self):
        self.listen()


class Window(QMainWindow):

    currentItem = None
    firstOpen = False

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

        self.captureKey = CaptureKey(self)
        self.captureKey.captureKeyState.connect(self.captureKeyClick)


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
        self.mediaPlayer.mediaChanged.connect(self.mediaChanged)
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
        if isinstance(item, QListWidgetItem):
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

    def captureKeyClick(self, state):
        print(state)
        if state == "prev":
            self.previousMusic()

        elif state == "play":
            self.play()

        elif state == "next":
            self.nextMusic()

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
        try:
            self.taskBarProgress.setValue(pos)

        except AttributeError as err:
            print(err)

    #mediaplayer signals
    def audioAvailableChanged(self, available):
        # if available == False:
        #     self.nextMusic()
        #     return

        if "Duration" in self.mediaPlayer.availableMetaData():
            self.playerWidget.setDuration(self.mediaPlayer.metaData("Duration"))
            self.taskBarProgress.setMaximum(self.mediaPlayer.metaData("Duration"))
            self.playListWidget.insertDuration(self.mediaPlayer.playlist().currentIndex(),
                                               self.mediaPlayer.metaData("Duration"))


        for data in self.mediaPlayer.availableMetaData():
            print(data, self.mediaPlayer.metaData(data))

    def currentMediaChanged(self, mediacontent):
        print(mediacontent.canonicalUrl())
        self.setWindowTitle(self.mediaPlayer.currentMedia().canonicalUrl().fileName())
        if self.currentItem:
            self.currentItem.setForeground(QBrush())
            self.currentItem.setBackground(QBrush())

        item = self.playListWidget.item(self.mediaPlayer.playlist().currentIndex())
        print(item)
        if isinstance(item, QListWidgetItem):
            item.setForeground(Qt.lightGray)
            item.setBackground(Qt.darkGray)
            self.currentItem = item

    # def durationChanged(self, duration):
    #     pass

    def mediaChanged(self, media):
        print(media)

    def mutedChanged(self, muted):
        if muted:
            self.playerWidget.mutedButtonStatus("muted")

        else:
            self.playerWidget.mutedButtonStatus("speaker")

    def positionChanged(self, pos):
        self.playerWidget.setPosition(pos)
        try:
            self.taskBarProgress.setValue(pos)

        except AttributeError as err:
            print(err)

    def seekableChanged(self, seekable):
        pass#print(seekable)

    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playerWidget.playButtonStatus("play")
            self.thumbnailPlayButton.setIcon(QIcon(":/icon/pausew.png"))

        elif state == QMediaPlayer.PausedState:
            self.playerWidget.playButtonStatus("pause")
            self.thumbnailPlayButton.setIcon(QIcon(":/icon/playw.png"))

        elif state == QMediaPlayer.StoppedState:
            self.playerWidget.playButtonStatus("pause")
            self.thumbnailPlayButton.setIcon(QIcon(":/icon/playw.png"))

    def volumeChanged(self, volume):
        pass#print(volume)

    def error(self, err):
        print(err, "asdasdasdasdasd")

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

    def showEvent(self, event):
        self.taskBarButton = QWinTaskbarButton(self)
        self.taskBarButton.setWindow(self.windowHandle())
        # self.taskBarButton.setOverlayIcon(QIcon(":/icon/disk.svg"))

        self.taskBarProgress = self.taskBarButton.progress()
        self.taskBarProgress.setVisible(True)

        self.thumbnailToolBar = QWinThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())

        self.thumbnailPreviousButton = QWinThumbnailToolButton(self.thumbnailToolBar)
        self.thumbnailPreviousButton.setIcon(QIcon(":/icon/previousw.png"))
        self.thumbnailPreviousButton.clicked.connect(self.previousMusic)

        self.thumbnailPlayButton = QWinThumbnailToolButton(self.thumbnailToolBar)
        self.thumbnailPlayButton.setIcon(QIcon(":/icon/playw.png"))
        self.thumbnailPlayButton.clicked.connect(self.play)

        self.thumbnailNextButton = QWinThumbnailToolButton(self.thumbnailToolBar)
        self.thumbnailNextButton.setIcon(QIcon(":/icon/nextw.png"))
        self.thumbnailNextButton.clicked.connect(self.nextMusic)

        self.thumbnailToolBar.addButton(self.thumbnailPreviousButton)
        self.thumbnailToolBar.addButton(self.thumbnailPlayButton)
        self.thumbnailToolBar.addButton(self.thumbnailNextButton)

        self.captureKey.start()


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