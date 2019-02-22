# -*- coding: utf-8 -*-
"""
Created on Fri Feb 22 17:31:05 2019

@author: Feng-cong Li
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout)



app = QApplication(sys.argv)
win = QWidget()

vlayout = QVBoxLayout()
win.setLayout(vlayout)

upper_layout = QHBoxLayout()
vlayout.addLayout(upper_layout)

disp_edit = QTextEdit()
source_edit = QTextEdit()

def on_source_change():
    code = source_edit.toPlainText()
    disp_edit.setHtml(code)

disp_edit.setReadOnly(True)
source_edit.textChanged.connect(on_source_change)

upper_layout.addWidget(disp_edit)
upper_layout.addWidget(source_edit)

win.show()

sys.exit(app.exec())