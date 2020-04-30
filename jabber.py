import sys
from jabber.gui.main_window import MainWindow
from PyQt5 import QtWidgets

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mw = MainWindow()
    mw.show()

    sys.exit(app.exec())
