from jabber.gui import MWBase, MWForm


class MainWindow(MWBase, MWForm):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
