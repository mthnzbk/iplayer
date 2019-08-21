from PyQt5.QtCore import QSettings


def settings():
    return QSettings("iplayer.ini", QSettings.IniFormat)