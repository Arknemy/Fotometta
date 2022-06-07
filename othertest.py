import sys

from PyQt5.QtWidgets import *

class App(QMainWindow):
    def __init__(self):
        super(App, self).__init__()

        centralWidget = QWidget()
        lay = QVBoxLayout(centralWidget)

        tab = QTabWidget()
        lay.addWidget(tab)
        for i in range(5):
            page = QWidget()
            tab.addTab(page, 'tab{}'.format(i))

        self.setCentralWidget(centralWidget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())






