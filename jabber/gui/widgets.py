from jabber.gui import ImgBase, ImgForm


class ImageWidget(ImgBase, ImgForm):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
