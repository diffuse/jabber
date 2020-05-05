from PyQt5 import uic

ui_path = 'jabber/gui/ui'
ClassListForm, ClassListBase = uic.loadUiType(f'{ui_path}/class_list.ui')
ImgForm, ImgBase = uic.loadUiType(f'{ui_path}/image.ui')
ImgListForm, ImgListBase = uic.loadUiType(f'{ui_path}/image_list.ui')
MicForm, MicBase = uic.loadUiType(f'{ui_path}/mic.ui')
MWForm, MWBase = uic.loadUiType(f'{ui_path}/main_window.ui')
