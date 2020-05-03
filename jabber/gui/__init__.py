from PyQt5 import uic

ui_path = 'jabber/gui/ui'
ImgForm, ImgBase = uic.loadUiType(f'{ui_path}/image.ui')
ImgListForm, ImgListBase = uic.loadUiType(f'{ui_path}/image_list.ui')
MWForm, MWBase = uic.loadUiType(f'{ui_path}/main_window.ui')
