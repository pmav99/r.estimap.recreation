"""
@package gui_core.forms

@brief Construct the core of pyqt GUI based on GRASS command interface
description.

Classes:
 - forms::NewGUI

This program is just a coarse approach to automatically build a GUI
from a xml-based GRASS user interface description.

You need to have Python 2.7, PyQt4 and python-xml.

The XML stream is read from executing the command given in the
command line, thus you may call it for instance this way:

python forms.py v.buffer

Or you set an alias or wrap the call up in a nice shell script, GUI
environment ... please contribute your idea.

Copyright(C) 2016 by the GRASS Development Team

This program is free software under the GPL(>=v2) Read the file
COPYING coming with GRASS for details.

@author Ondrej Pesek <pesej.ondrek@gmail.com>
"""

import sys
import os
import re

from parameters import Parameters as newWidget
from parameters import Factory

from PyQt4 import QtGui
from PyQt4.QtCore import *
from grass.script import task as gtask
from grass.script import run_command


GUIDIR = os.path.join(os.getenv("GISBASE"), "gui")
ICONDIR = os.path.join(GUIDIR, "icons")
IMGDIR = os.path.join(GUIDIR, "images")


class NewGUI(QtGui.QMainWindow):
    def __init__(self, module, parent=None):
        """
        constructor
        :param module: called module
        """

        app = QtGui.QApplication([])
        super(NewGUI, self).__init__(parent)

        self.setWindowTitle(self.get_title(module))
        icon = QtGui.QIcon(os.path.join(ICONDIR, 'grass-48x48.png'))
        self.setWindowIcon(icon)
        self.create_gui(module)

        self.show()
        sys.exit(app.exec_())

    def create_gui(self, module):
        """
        sets description, tabs, buttons and code_string into the main window
        :param module: called module
        """

        tabs, code_string = self.get_tabs(module)

        box = QtGui.QVBoxLayout()
        box.addWidget(self.get_description(module))
        box.addWidget(tabs)
        box.addWidget(self.basic_buttons(module, code_string))
        box.addWidget(self.horizontal_line())
        box.addWidget(code_string)
        box.setSpacing(10)
        complete_gui = QtGui.QWidget()
        complete_gui.setLayout(box)
        # print complete_gui.size()
        # self.resize(self.minimumSize())

        self.setCentralWidget(complete_gui)

        # self.setFixedHeight(300)
        # print complete_gui.size()

    def get_tabs(self, module):
        """
        parse individual widgets, create tabs and put widgets into those tabs
        :param module: called module
        :return: tabs, code_string (widget with code string that user can see)
        """

        tabs = QtGui.QTabWidget()

        page_required = QtGui.QWidget()
        box_required = QtGui.QVBoxLayout()
        boxs = {}

        page_optional = QtGui.QWidget()
        box_optional = QtGui.QVBoxLayout()
        pages = {}

        page_section = {}
        boxs_section = {}

        self.codeDict = {}
        self.flagList = []
        code_string = QtGui.QTextEdit(module)
        code_string.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        code_string.setReadOnly(True)
        code_string.setFixedHeight(QtGui.QLineEdit().sizeHint().height()*2)

        fact = Factory()

        # tabs for params
        for task in gtask.command_info(module)['params']:

            widget = newWidget(task, module, self.codeDict, self.flagList,
                               code_string, fact).new_widget()

            if task['guisection']:
                try:
                    page_section[task['guisection']]
                except:
                    page = QtGui.QWidget()
                    box = QtGui.QVBoxLayout()
                    page_section.update({task['guisection']: page})
                    boxs_section.update({task['guisection']: box})
                    pages.update({task['guisection']:
                                 page_section[task['guisection']]})
                    boxs.update({task['guisection']:
                                boxs_section[task['guisection']]})
                boxs[task['guisection']].addWidget(widget)

            elif task['required'] is True:
                try:
                    pages.update({'Required': page_required})
                    boxs.update({'Required': box_required})
                except:
                    pass
                boxs['Required'].addWidget(widget)

            else:
                try:
                    pages.update({'Optional': page_optional})
                    boxs.update({'Optional': box_optional})
                except:
                    pass
                boxs['Optional'].addWidget(widget)

        # tabs for flags
        for task in gtask.command_info(module)['flags']:

            widget = newWidget(task, module, self.codeDict, self.flagList,
                               code_string, fact).new_widget()
            if task['guisection']:
                try:
                    page_section[task['guisection']]
                except:
                    page = QtGui.QWidget()
                    box = QtGui.QVBoxLayout()
                    page_section.update({task['guisection']: page})
                    boxs_section.update({task['guisection']: box})
                    pages.update({task['guisection']:
                                 page_section[task['guisection']]})
                    boxs.update({task['guisection']:
                                boxs_section[task['guisection']]})
                boxs[task['guisection']].addWidget(widget)

            else:
                try:
                    pages.update({'Optional': page_optional})
                    boxs.update({'Optional': box_optional})
                except:
                    pass
                if not task['name'] == 'help':
                    boxs['Optional'].addWidget(widget)
                    # we don't have to see help everywhere

        for i in pages:
            boxs[i].addStretch()
            layout = boxs[i]
            layout.setSpacing(0)
            widget = QtGui.QWidget()
            widget.setLayout(layout)

            a = QtGui.QScrollArea()
            palette = a.palette()
            palette.setColor(
                a.backgroundRole(),
                QtGui.QLineEdit().palette().color(QtGui.QLineEdit().
                                                  backgroundRole()))
            a.setPalette(palette)
            a.setWidget(widget)
            a.setWidgetResizable(True)
            a.setFrameShape(QtGui.QFrame.NoFrame)
            a.setAutoFillBackground(True)
            a.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            a.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

            new_layout = QtGui.QVBoxLayout()
            new_layout.addWidget(a)
            new_layout.setContentsMargins(1, 1, 1, 1)

            pages[i].setLayout(new_layout)

        if box_required:
            tabs.addTab(page_required, 'Required')
        for i in page_section:
            tabs.addTab(pages[i], i)
        tabs.addTab(page_optional, 'Optional')

        return tabs, code_string

    def get_title(self, module):
        """
        create title of main window
        :param module: called module
        :return: new title of the window with parameters
        """

        self.title = [p for p in gtask.command_info(module)['keywords']]
        self.title = re.sub("'", "", module + " " + str(self.title))
        return self.title

    def get_description(self, module):
        """
        creates description with logo
        :param module: called module
        :return: label with module description
        """

        logo = QtGui.QLabel()
        logo.setPixmap(QtGui.QPixmap(os.path.join(IMGDIR, 'grass_form.png')))
        logo.setFixedWidth(logo.sizeHint().width())
        text = QtGui.QLabel(gtask.command_info(module)['description'])
        text.setWordWrap(True)

        layout = QtGui.QHBoxLayout()
        layout.addWidget(logo)
        layout.addWidget(text)
        layout.setContentsMargins(0, 0, 0, 0)

        description = QtGui.QWidget()
        description.setLayout(layout)
        description.setFixedHeight(description.sizeHint().height())

        return description

    def basic_buttons(self, module, code_string):
        """
        create buttons to close window, raise help and run or copy cmd
        :param module: called module
        :param code_string: widget with code string that user can see
        :return: layout with buttons
        """

        close_button = QtGui.QPushButton('Close')
        run_button = QtGui.QPushButton('Run')
        run_button.setStyleSheet('QPushButton {color: green;}')
        copy_button = QtGui.QPushButton('Copy')
        help_button = QtGui.QPushButton('Help')

        layout = QtGui.QHBoxLayout()
        layout.addWidget(close_button)
        layout.addWidget(run_button)
        layout.addWidget(copy_button)
        layout.addWidget(help_button)
        buttons = QtGui.QWidget()
        buttons.setLayout(layout)

        close_button.clicked.connect(lambda: self.close())
        help_button.clicked.connect(lambda: run_command(module, 'help'))
        run_button.clicked.connect(lambda: self.run_command(module))

        clipboard = QtGui.QApplication.clipboard()
        copy_button.clicked.connect(lambda: self.copy_text(clipboard,
                                                           code_string))

        return buttons

    def horizontal_line(self):
        """
        creates a horizontal line to separate the code_string
        :return: horizontal line
        """

        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        return line

    def copy_text(self, clipboard, code_string):
        """
        This method copies the cmd string to clipboard
        :param clipboard: system clipboard
        :param code_string: widget with code string that user can see
        """

        clipboard.clear()
        clipboard.setText(code_string.toPlainText())

    def run_command(self, module):
        """
        runs the command
        :param module: called module
        """

        flags = ''
        long_flags = {}
        for i in self.flagList:
            if len(i) == 1:
                flags = flags + i
            else:
                long_flags.update({i: True})

        if long_flags:
            params_long_flags = {}
            params_long_flags.update(long_flags)
            params_long_flags.update(self.codeDict)
            run_command(module, flags=flags, **params_long_flags)
        else:
            run_command(module, flags=flags, **self.codeDict)
