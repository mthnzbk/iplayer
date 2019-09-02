from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QSlider, QVBoxLayout, QSpacerItem, QListWidget,
                               QAbstractItemView, QListWidgetItem, QListView, QStyle, QSizePolicy, QLabel)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from settings import settings


class MusicSlider(QSlider):
    def mousePressEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))
        self.sliderMoved.emit(int((event.x() / self.width()) * self.maximum()))

    def mouseMoveEvent(self, event):
        self.setValue(QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), event.x(), self.width()))
        self.sliderMoved.emit(int((event.x() / self.width()) * self.maximum()))


class Button(QPushButton):
    def __init__(self, parent, type):
        super().__init__()
        self.type = type
        self.setFlat(True)

    def mousePressEvent(self, event):
        self.setIcon(QIcon(f":/icon/{self.type}_press.png"))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setIcon(QIcon(f":/icon/{self.type}.png"))
        super().mouseReleaseEvent(event)

    def setButtonType(self, type):
        self.type = type


class PlayerWidget(QWidget):

    musicPositionMoved = pyqtSignal(int)
    repeatButtonClicked = pyqtSignal()
    mixedButtonClicked = pyqtSignal()
    previousButtonClicked = pyqtSignal()
    playButtonClicked = pyqtSignal()
    nextButtonClicked = pyqtSignal()
    mutedButtonClicked = pyqtSignal()
    volumeChanged = pyqtSignal(int)
    showOrHideClicked = pyqtSignal()

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(120)
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(12)
        # self.layout().setContentsMargins(0, 0, 0, 0)

        self.musicSlider = MusicSlider(self)
        self.musicSlider.sliderMoved.connect(lambda : self.musicPositionMoved.emit(self.musicSlider.value()))
        self.musicSlider.setOrientation(Qt.Horizontal)
        self.layout().addWidget(self.musicSlider)

        self.buttonsLayout = QHBoxLayout(self)
        self.layout().addLayout(self.buttonsLayout)

        self.repeatButton = Button(self, "loop")
        self.repeatButton.setFixedSize(QSize(18, 18))
        self.repeatButton.setIconSize(QSize(18, 18))
        self.repeatButton.clicked.connect(lambda: self.repeatButtonClicked.emit())
        self.repeatButton.setIcon(QIcon(":/icon/loop.png"))
        self.repeatButton.setStyleSheet("border: none;")
        self.buttonsLayout.addWidget(self.repeatButton)

        self.mixedButton = Button(self, "shuffle")
        self.mixedButton.setFixedSize(QSize(18, 18))
        self.mixedButton.setIconSize(QSize(18, 18))
        self.mixedButton.clicked.connect(lambda: self.mixedButtonClicked.emit())
        self.mixedButton.setIcon(QIcon(":/icon/shuffle.png"))
        self.mixedButton.setStyleSheet("border: none;")
        self.buttonsLayout.addWidget(self.mixedButton)

        self.buttonsLayout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.previousButton = Button(self, "previous")
        self.previousButton.setFixedSize(QSize(24, 24))
        self.previousButton.setIconSize(QSize(24, 24))
        self.previousButton.clicked.connect(lambda : self.previousButtonClicked.emit())
        self.previousButton.setIcon(QIcon(":/icon/previous.png"))
        self.previousButton.setStyleSheet("border: none;")
        self.buttonsLayout.addWidget(self.previousButton)

        self.playOrStopButton = Button(self, "play")
        self.playOrStopButton.setFixedSize(QSize(64, 64))
        self.playOrStopButton.setIconSize(QSize(64, 64))
        self.playOrStopButton.setIcon(QIcon(":/icon/play.png"))
        self.playOrStopButton.setStyleSheet("border: none;")
        self.playOrStopButton.clicked.connect(lambda: self.playButtonClicked.emit())
        self.buttonsLayout.addWidget(self.playOrStopButton)

        self.nextButton = Button(self, "next")
        self.nextButton.setFixedSize(QSize(24, 24))
        self.nextButton.setIconSize(QSize(24, 24))
        self.nextButton.clicked.connect(lambda : self.nextButtonClicked.emit())
        self.nextButton.setIcon(QIcon(":/icon/next.png"))
        self.nextButton.setStyleSheet("border: none;")
        self.buttonsLayout.addWidget(self.nextButton)

        self.buttonsLayout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Minimum))

        self.mutedButton = Button(self, "speaker")
        self.mutedButton.setFixedSize(QSize(18, 18))
        self.mutedButton.setIconSize(QSize(18, 18))
        self.mutedButton.setIcon(QIcon(":/icon/speaker.png"))
        self.mutedButton.setStyleSheet("border: none;")
        self.mutedButton.clicked.connect(lambda : self.mutedButtonClicked.emit())

        self.volumeSlider = QSlider(self)
        self.volumeSlider.setFixedWidth(64)
        self.volumeSlider.valueChanged.connect(lambda : self.volumeChanged.emit(self.volumeSlider.value()))
        self.volumeSlider.setMaximum(100)
        self.volumeSlider.setOrientation(Qt.Horizontal)
        self.volumeSlider.setValue(int(settings().value("volume") or 100))
        self.volumeSlider.setStyleSheet("border: none;")

        self.buttonsLayout.addWidget(self.mutedButton)
        self.buttonsLayout.addWidget(self.volumeSlider)

        self.showOrHidePlayList = Button(self, "playlist")
        self.showOrHidePlayList.setFixedSize(QSize(16, 16))
        self.showOrHidePlayList.setIconSize(QSize(16, 16))
        self.showOrHidePlayList.setIcon(QIcon(":/icon/playlist.png"))
        self.showOrHidePlayList.setStyleSheet("border: none;")
        self.showOrHidePlayList.clicked.connect(lambda: self.showOrHideClicked.emit())
        self.buttonsLayout.addWidget(self.showOrHidePlayList)

        playback = int(settings().value("playbackMode") or 2)
        self.repeatButtonStatus(playback)

    def setDuration(self, duration):
        self.musicSlider.setMaximum(duration)

    def setPosition(self, position):
        self.musicSlider.setValue(position)

    def repeatButtonStatus(self, playback):
        if playback == 1:
            self.repeatButton.setIcon(QIcon(":/icon/current.png"))
            self.repeatButton.setButtonType("current")

        elif playback == 2:
            self.repeatButton.setIcon(QIcon(":/icon/sequential.png"))
            self.repeatButton.setButtonType("squential")

        elif playback == 3:
            self.repeatButton.setIcon(QIcon(":/icon/loop.png"))
            self.repeatButton.setButtonType("loop")

    def playButtonStatus(self, status):
        if status == "pause":
            self.playOrStopButton.setIcon(QIcon(":/icon/play.png"))
            self.playOrStopButton.setButtonType("play")

        elif status == "play":
            self.playOrStopButton.setIcon(QIcon(":/icon/pause.png"))
            self.playOrStopButton.setButtonType("pause")

    def mutedButtonStatus(self, status):
        if status == "muted":
            self.mutedButton.setButtonType("speaker_muted")
            self.mutedButton.setIcon(QIcon(":/icon/speaker_muted.png"))

        elif status == "speaker":
            self.mutedButton.setButtonType("speaker")
            self.mutedButton.setIcon(QIcon(":/icon/speaker.png"))


class PlayListWidget(QListWidget):

    musicDrop = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setMovement(QListView.Free)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


    def dropEvent(self, event):
        # event.setDropAction(Qt.MoveAction)
        self.musicDrop.emit(event.mimeData().urls())
        # event.accept()
        super().dropEvent(event)

    def dragEnterEvent(self, event):
        event.accept()
        # super().dragEnterEvent(event)

    def dragLeaveEvent(self, event):
        event.accept()
        # super().dragLeaveEvent(event)

    def dragMoveEvent(self, event):
        event.accept()
        # super().dragMoveEvent(event)

    def addMusic(self, music):
        item = QListWidgetItem()

        playListItem = PlayListItem(self)
        playListItem.setText(music.fileName())
        item.setSizeHint(playListItem.sizeHint())

        self.addItem(item)
        self.setItemWidget(item, playListItem)

    def addMusics(self, musics):
        for url in musics:
            item = QListWidgetItem()
            item.setTextAlignment(Qt.AlignLeft)

            playListItem = PlayListItem(self)
            playListItem.setText(url.fileName())
            item.setSizeHint(playListItem.minimumSizeHint())

            self.addItem(item)
            self.setItemWidget(item, playListItem)

    def insertDuration(self, index, duration):
        item = self.itemWidget(self.item(index))
        item.setDuration(duration)


class PlayListItem(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setLayout(QHBoxLayout())

        self.itemNameLabel = QLabel(self)
        self.itemNameLabel.setWordWrap(True)
        self.layout().addWidget(self.itemNameLabel)
        # self.layout().addSpacerItem(QSpacerItem(10, 5, QSizePolicy.Preferred, QSizePolicy.Preferred))

        self.durationLabel = QLabel(self)
        self.durationLabel.setFixedWidth(40)
        self.durationLabel.setAlignment(Qt.AlignRight)
        self.layout().addWidget(self.durationLabel)

    def setText(self, text):
        self.itemNameLabel.setText(text)

    def setDuration(self, duration):
        self.durationLabel.setText(self.__duration2time(duration))


    def __duration2time(self, duration):
        m = duration/1000
        time = "{:02d}:{:02d}".format(int(m/60), int(m%60))

        return time