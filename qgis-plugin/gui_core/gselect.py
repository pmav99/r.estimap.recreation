"""
@package gui_core.gselect

@brief Complex widget elements of PyQt based GUI of GRASS

Classes:
 - :class:'TreeComboBox'
 - :class:'BrowseFile'
 - :class:'MultipleValues'
 - :class:'Layers'
 - :class:'Colums'
 - :class:'Colors'
 - :class:'DbTable'
 - :class:'Mapsets'
 - :class:'Locations'
 - :class:'SimpleValues'
 - :class:'Quiet'

(C) 2016 by the GRASS Development Team

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author Ondrej Pesek <pesej.ondrek@gmail.com>
"""

from PyQt4.QtCore import QModelIndex, QEvent, Qt, QSize
from PyQt4 import QtGui
from grass import script
import subprocess
import glob
import os


class TreeComboBox(QtGui.QComboBox):
    """
    widget for tree view models
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer, parent=None):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(TreeComboBox, self).__init__(parent)

        self.__skip_next_hide = False

        tree_view = QtGui.QTreeView(self)
        tree_view.setFrameShape(QtGui.QFrame.NoFrame)
        tree_view.setEditTriggers(tree_view.NoEditTriggers)
        tree_view.setAlternatingRowColors(True)
        tree_view.setSelectionBehavior(tree_view.SelectRows)
        # tree_view.setWordWrap(True)
        tree_view.setAllColumnsShowFocus(True)
        self.setView(tree_view)
        self.setEditable(True)
        self.setModel(self.get_model(gtask))
        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer,
            code_string_changer))  # see in parameters.py

        self.view().viewport().installEventFilter(self)

    def showPopup(self):
        self.setRootModelIndex(QModelIndex())
        super(TreeComboBox, self).showPopup()

    def hidePopup(self):
        self.setRootModelIndex(self.view().currentIndex().parent())
        # self.setCurrentIndex(self.view().currentIndex().row())
        if self.__skip_next_hide:
            self.__skip_next_hide = False
        else:
            super(TreeComboBox, self).hidePopup()

    def select_index(self, index):
        self.setRootModelIndex(index.parent())
        self.setCurrentIndex(index.row())

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonPress and object is \
                self.view().viewport():
            index = self.view().indexAt(event.pos())
            self.__skip_next_hide = not self.view().visualRect(index).\
                contains(event.pos())
        return False

    def get_model(self, gtask):
        """
        creates the core of a tree based model to input into widget
        :param gtask: part of gtask for this widget
        :return: tree model
        """
        mapsets = script.mapsets(search_path=True)
        model = QtGui.QStandardItemModel()
        # model.__init__(parent=None)
        model.setParent(self)
        for mapset in mapsets:
            parent_item = QtGui.QStandardItem('Mapset: '+mapset)
            parent_item.setSelectable(False)
            list = script.core.list_pairs(gtask['prompt'])
            for map in list:
                if mapset in map:
                    parent_item.appendRow(QtGui.QStandardItem
                                          ('%s@%s' % (map[0], map[1])))
            model.appendRow(parent_item)

        return model


class BrowseFile(QtGui.QWidget):
    """
    widget that allows user to choose path to file or directory
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer, parent=None):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(BrowseFile, self).__init__(parent)
        self.gtask = gtask

        layout = QtGui.QHBoxLayout()
        self.line = QtGui.QLineEdit()
        button = QtGui.QPushButton('Browse')
        button.clicked.connect(self.select_file)

        button.setMinimumSize(button.sizeHint())
        self.line.setMinimumSize(self.line.sizeHint())

        layout.addWidget(self.line)
        layout.addWidget(button)
        self.setLayout(layout)

        self.line.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self.line, code_dict_changer,
            code_string_changer))  # see in parameters.py

    def select_file(self):
        """
        raise dialog to choose file or directory
        """

        if self.gtask['prompt'] == 'file':
            file_path = QtGui.QFileDialog.getOpenFileName(self, 'Select file')
        else:
            file_path = QtGui.QFileDialog.getExistingDirectory(
                self, 'Select directory')
        if file_path:
            self.line.setText(file_path)
        else:
            return


class MultipleValues(QtGui.QGroupBox):
    """
    widget that allows user to choose predefined values (even more than one)
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(MultipleValues, self).__init__()

        default_boxes = gtask['default'].split(',')

        i = 0
        if not gtask['values_desc']:
            layout = QtGui.QHBoxLayout()
            for item in gtask['values']:
                box = QtGui.QCheckBox(item)
                box.setObjectName(gtask['values'][i])
                if box.objectName() in default_boxes:
                    box.setChecked(True)
                layout.addWidget(box)
                box.stateChanged.connect(lambda: self.change_command(
                    gtask, flag_list, layout, code_dict_changer,
                    code_string_changer))  # see in parameters.py
                i = i+1
        else:
            layout = QtGui.QVBoxLayout()
            layout.setSpacing(0)
            for item in gtask['values_desc']:
                box = QtGui.QCheckBox(item)
                box.setObjectName(gtask['values'][i])
                if box.objectName() in default_boxes:
                    box.setChecked(True)
                layout.addWidget(box)
                box.stateChanged.connect(lambda: self.change_command(
                    gtask, flag_list, layout, code_dict_changer,
                    code_string_changer))  # see in parameters.py
                i = i+1

        layout.addStretch()
        self.setLayout(layout)


class Layers(QtGui.QComboBox):
    """
    widget that allows user to choose from layers in chosen map (input, map)
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Layers, self).__init__()

        self.setEditable(True)

        self.gtask = gtask
        self.code_dict = code_dict

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_layers(self):
        """
        load layers (based on map in input or map widget)
        """

        self.clear()

        if self.gtask['element'] == 'layer_all':
            self.addItem('-1')

        try:
            layers = script.vector_db(map=self.code_dict['input'])
            for layer in layers:
                self.addItem(str(layer))
        except:
            try:
                layers = script.vector_db(map=self.code_dict['map'])
                for layer in layers:
                    self.addItem(str(layer))
            except:
                if self.count() == 0:
                    self.addItem('')

    def showPopup(self):
        text = self.currentText()
        self.get_layers()
        super(Layers, self).showPopup()
        if text in [self.itemText(i) for i in range(self.count())]:
            self.setEditText(text)
        else:
            self.setEditText('')


class Columns(QtGui.QComboBox):
    """
    widget that allows user to choose from columns in chosen map and layer
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Columns, self).__init__()

        self.setEditable(True)

        # self.gtask = gtask
        self.code_dict = code_dict

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_layer(self):
        """
        transforming layer into int (if it is)
        :return: name of layer (int, string)
        """

        try:
            layer = int(self.code_dict['layer'])
            return layer
        except:
            return self.code_dict['layer']

    def get_columns(self, layers, layer):
        """
        load columns
        :param layers: dictionary of all layers in map
        :param layer: layer chosen in widget Layer
        """

        for item in script.db_describe(
                table=layers[layer]["table"],
                driver=layers[layer]["driver"],
                database=layers[layer]["database"])['cols']:
            self.addItem(item[0])

    def set_values(self):
        """
        setting columns into the widget
        """

        self.clear()

        try:
            layers = script.vector_db(map=self.code_dict['input'])
            layer = self.get_layer()

            if layer == -1:
                for layer in layers.keys():
                    self.get_columns(layers, layer)
            else:
                self.get_columns(layers, layer)
        except:
            try:
                layers = script.vector_db(map=self.code_dict['map'])
                layer = self.get_layer()

                if layer == -1:
                    for layer in layers.keys():
                        self.get_columns(layers, layer)
                else:
                    self.get_columns(layers, layer)
            except:
                self.addItem('')

    def showPopup(self):

        text = self.currentText()
        self.set_values()

        super(Columns, self).showPopup()
        if text in [self.itemText(i) for i in range(self.count())]:
            self.setEditText(text)
        else:
            self.setEditText('')


class Colors(QtGui.QWidget):
    """
    widget that allows user to choose color from color dialog
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Colors, self).__init__()

        layout = QtGui.QHBoxLayout()
        self.colorBtn = QtGui.QPushButton()

        self.btnStyle = 'border-style: double; border-width: 3px; ' \
                        'border-color: beige; min-width: 8em; padding: 6px'

        if gtask['default'] == 'none':
            self.colorBtn.setStyleSheet(
                "QPushButton {background-color: #c8c8c8;%s}" % self.btnStyle)
            self.colorBtn.setText('Select color')
            layout.addWidget(self.colorBtn)
            transparent = QtGui.QCheckBox('Transparent')
            transparent.stateChanged.connect(lambda: self.change_command(
                gtask, flag_list, layout, code_dict_changer,
                code_string_changer))
            layout.addWidget(transparent)
        else:
            splitted_color = gtask['default'].split(':')
            if len(splitted_color) > 1:
                color_name = '#%02x%02x%02x' % (
                    int(splitted_color[0]), int(splitted_color[1]),
                    int(splitted_color[2]))
            else:
                color_name = gtask['default']

            if QtGui.QColor(color_name).red() + \
                    QtGui.QColor(color_name).blue() + \
                    QtGui.QColor(color_name).green() < 387:
                text_color = 'white'
            else:
                text_color = 'black'

            self.colorBtn.setStyleSheet("QPushButton {background-color: %s;"
                                        "color: %s; %s}"
                                        % (color_name, text_color,
                                           self.btnStyle))
            self.colorBtn.setText(gtask['default'])
            layout.addWidget(self.colorBtn)

        layout.addStretch()

        self.setLayout(layout)

        self.colorBtn.clicked.connect(lambda: self.color_picker(
            gtask, flag_list, layout, code_dict_changer, code_string_changer))

    def color_picker(self, gtask, flag_list, layout, code_dict_changer,
                     code_string_changer):
        """
        raising the color dialog and painting color into button
        """

        color = QtGui.QColorDialog.getColor(
            initial=QtGui.QColor(self.colorBtn.palette().
                                 color(QtGui.QPalette.Background)))
        if color.isValid():
            if color.red() + color.green() + color.blue() < 387:
                text_color = 'white'
            else:
                text_color = 'black'
            self.colorBtn.setStyleSheet("QPushButton { background-color: %s;"
                                        "color: %s; %s}"
                                        % (color.name(), text_color,
                                           self.btnStyle))
            self.colorBtn.setText('%s:%s:%s' % (color.red(), color.green(),
                                                color.blue()))
            self.change_command(gtask, flag_list, layout, code_dict_changer,
                                code_string_changer)


class DbTable(QtGui.QComboBox):
    """
    widget that allows user to choose db table
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(DbTable, self).__init__()
        self.code_dict = code_dict

        self.setEditable(True)

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_db_info(self):
        """
        check if there is defined driver or database
        :return: driver and database (default or defined)
        """

        try:
            driver = self.code_dict['driver']
            try:
                database = self.code_dict['database']
            except:
                connect = script.db_connection()
                database = connect['database']
        except:
            connect = script.db_connection()
            try:
                database = self.code_dict['database']
                driver = connect['driver']
            except:
                database = connect['database']
                driver = connect['driver']

        return driver, database

    def get_tables(self):
        """
        get tables from user's database
        :return: tables in one string
        """

        driver, database = self.get_db_info()

        tables = script.start_command('db.tables',
                                      flags='p',
                                      driver=driver,
                                      database=database,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)

        return tables.communicate()[0]

    def showPopup(self):

        text = self.currentText()
        tables = self.get_tables()

        self.clear()
        if tables:
            for table in tables.splitlines():
                self.addItem(table)
        else:
            self.addItem('')

        super(DbTable, self).showPopup()
        if text in [self.itemText(i) for i in range(self.count())]:
            self.setEditText(text)
        else:
            self.setEditText('')


class Mapsets(QtGui.QComboBox):
    """
    widget that allows user to choose mapset from combobox
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Mapsets, self).__init__()
        self.code_dict = code_dict

        self.setEditable(True)

        mapsets = self.get_mapsets().split(' ')
        self.addItems(mapsets)

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_mapsets(self):
        """
        load mapsets when location, dbase, both or nothing is defined
        :return: mapsets in one string
        """

        try:
            try:  # exists both location and dbase
                mapsets = script.start_command(
                    'g.mapset', flags='l', location=self.code_dict['location'],
                    dbase=self.code_dict['dbase'], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

                return mapsets.communicate()[0].splitlines()[0]
            except:
                try:  # just location
                    mapsets = script.start_command(
                        'g.mapset', flags='l',
                        location=self.code_dict['location'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    return mapsets.communicate()[0].splitlines()[0]
                except:  # just dbase
                    mapsets = script.start_command(
                        'g.mapset', flags='l', dbase=self.code_dict['dbase'],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    return mapsets.communicate()[0].splitlines()[0]
        except:  # no dependencies defined
            mapsets = script.start_command('g.mapsets',
                                           flags='l',
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)

            return mapsets.communicate()[0].splitlines()[0]

    def showPopup(self):

        text = self.currentText()

        self.clear()
        items = self.get_mapsets().split(' ')

        if items[len(items)-1] == '':
            del items[len(items)-1]

        self.addItems(items)

        super(Mapsets, self).showPopup()
        if text in [self.itemText(i) for i in range(self.count())]:
            self.setEditText(text)
        else:
            self.setEditText('')


class Locations(QtGui.QComboBox):
    """
    widget that allows user to choose location from combobox
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Locations, self).__init__()
        self.code_dict = code_dict

        self.setEditable(True)

        self.addItems(self.get_locations())

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_locations(self):
        """
        find locations in path (default or defined in dbase)
        :return: list of locations
        """

        locations = []

        try:
            db_path = self.code_dict['dbase']
        except:
            db_path = script.gisenv()['GISDBASE']

        for location in glob.glob(os.path.join(
                    db_path, "*")):
                if os.path.join(location, "PERMANENT") in \
                        glob.glob(os.path.join(location, "*")):
                    locations.append(os.path.basename(location))

        return locations

    def showPopup(self):

        text = self.currentText()

        self.clear()
        items = self.get_locations()

        if items:
            self.addItems(items)
        else:
            self.addItem('')

        super(Locations, self).showPopup()
        if text in [self.itemText(i) for i in range(self.count())]:
            self.setEditText(text)
        else:
            self.setEditText('')


class SimpleValues(QtGui.QWidget):
    """
    widget for gui item with values (user can select just one)
    basic is just combobox, all the methods are for icon choosing widget
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(SimpleValues, self).__init__()
        self.gtask = gtask

        layout = QtGui.QHBoxLayout()

        if gtask['name'] != 'icon':
            self.widget = QtGui.QComboBox()
            self.widget.setEditable(True)
            self.widget.addItems(gtask['values'])

            if gtask['default']:
                self.widget.setEditText(gtask['default'])

            self.widget.textChanged.connect(lambda: self.change_command(
                gtask, flag_list, self.widget,
                code_dict_changer, code_string_changer))

            layout.addWidget(self.widget)
        else:  # special widget for
            self.icons_path = os.path.join(os.getenv("GISBASE"),
                                           "gui", "images", "symbols")

            self.widget = QtGui.QPushButton()

            if gtask['default']:
                self.widget.setText(gtask['default'])
                self.widget.setIcon(QtGui.QIcon(
                    os.path.join(self.icons_path, gtask['default']+'.png')))
            else:
                self.widget.setText('Select symbol')

            self.widget.setIconSize(QSize(30, 30))

            self.widget.clicked.connect(lambda: self.get_dialog(
                gtask, code_dict, flag_list, code_dict_changer,
                code_string_changer))

            layout.addWidget(self.widget)
            layout.addStretch()

        self.setLayout(layout)

    def get_dialog(self, gtask, code_dict, flag_list, code_dict_changer,
                   code_string_changer):
        """
        raise dialog for choosing icon
        """

        # app = QtGui.QApplication([])
        self.dialog = QtGui.QDialog()

        self.set_layout(gtask, code_dict, flag_list, code_dict_changer,
                        code_string_changer)
        self.dialog.setFixedSize(QSize(300, 300))
        self.dialog.setWindowTitle('Select symbol')
        ICONDIR = os.path.join(os.getenv("GISBASE"), "gui", "icons",
                               "grass_dialog.ico")
        self.dialog.setWindowIcon(QtGui.QIcon(ICONDIR))

        self.dialog.show()
        # dialog.exec_()

    def set_layout(self, gtask, code_dict, flag_list, code_dict_changer,
                   code_string_changer):
        """
        set the dialog right layout with icons, iconsets and buttons
        """

        self.dialog_layout = QtGui.QVBoxLayout()

        iconsets = self.get_iconsets()
        symbol_name = self.get_symbol_name()

        buttons = self.get_buttons(gtask, code_dict, flag_list,
                                   code_dict_changer, code_string_changer)

        self.get_icons()

        self.iconsets.currentIndexChanged.connect(self.set_icons)

        self.dialog_layout.addWidget(iconsets)
        self.dialog_layout.addWidget(symbol_name)

        if self.iconsets.currentText():
            self.icons = QtGui.QWidget()
            icons_layout = QtGui.QGridLayout()
            row = 1
            column = 1
            for item in [
                self.icons_dict[str(self.iconsets.currentText())][i]
                for i in range(
                    len(self.icons_dict[str(self.iconsets.currentText())]))]:
                icons_layout.addWidget(item, row, column)
                if column < 5:
                    column = column+1
                else:
                    column = 1
                    row = row+1
            self.icons.setLayout(icons_layout)
        self.dialog_layout.addWidget(self.icons)

        self.dialog_layout.addWidget(buttons)

        self.dialog.setLayout(self.dialog_layout)

    def get_buttons(self, gtask, code_dict, flag_list, code_dict_changer,
                    code_string_changer):
        """
        create buttons with their signals
        :return: buttons
        """

        buttons = QtGui.QWidget()
        buttons_layout = QtGui.QHBoxLayout()

        self.ok = QtGui.QPushButton('OK')
        self.ok.setEnabled(False)
        cancel = QtGui.QPushButton('Cancel')

        self.ok.clicked.connect(lambda: self.dialog.close())
        self.ok.clicked.connect(lambda: self.change_icon(
            gtask, code_dict, flag_list, code_dict_changer,
            code_string_changer))
        cancel.clicked.connect(lambda: self.dialog.close())

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.ok)
        buttons_layout.addWidget(cancel)
        buttons.setLayout(buttons_layout)

        return buttons

    def get_iconsets(self):
        """
        create iconsets and load values (iconsets) into combobox
        :return: iconsets (title and combobox in one widget)
        """

        complete_widget = QtGui.QWidget()
        iconsets_layout = QtGui.QHBoxLayout()

        self.iconsets = QtGui.QComboBox()
        for icon in self.gtask['values']:
            iconset = icon.split('/')[0]
            if iconset not in [self.iconsets.itemText(i)
                               for i in range(self.iconsets.count())]:
                self.iconsets.addItem(iconset)
        index = self.iconsets.findText(self.widget.text().split('/')[0])
        self.iconsets.setCurrentIndex(index)

        iconsets_layout.addWidget(QtGui.QLabel('Symbol directory: '))
        iconsets_layout.addWidget(self.iconsets)
        iconsets_layout.addStretch()
        complete_widget.setLayout(iconsets_layout)

        return complete_widget

    def get_symbol_name(self):
        """
        creates widget which is showing the symbol name to user
        :return: static title and variable symbol name in one widget
        """

        complete_widget = QtGui.QWidget()
        symbol_name_layout = QtGui.QHBoxLayout()

        self.symbol = QtGui.QLabel()

        symbol_name_layout.addWidget(QtGui.QLabel('Symbol name: '))
        symbol_name_layout.addWidget(self.symbol)
        symbol_name_layout.addStretch()
        complete_widget.setLayout(symbol_name_layout)

        return complete_widget

    def set_icons(self):
        """
        set new icons after changing iconset
        """

        self.dialog_layout.removeWidget(self.icons)
        self.icons.hide()

        self.icons = QtGui.QWidget()
        icons_layout = QtGui.QGridLayout()
        row = 1
        column = 1
        for item in [
            self.icons_dict[str(self.iconsets.currentText())][i]
            for i in range(
                len(self.icons_dict[str(self.iconsets.currentText())]))]:
            icons_layout.addWidget(item, row, column)
            if column < 5:
                column = column+1
            else:
                column = 1
                row = row+1

        self.icons.setLayout(icons_layout)
        self.dialog_layout.insertWidget(2, self.icons)

    def get_icons(self):
        """
        creates dictionary where key is iconset and values are icons
        """

        self.icons_dict = {}
        iconset = None
        self.string_to_set = QtGui.QLabel()

        for full_value in self.gtask['values']:

            widget = QtGui.QPushButton()
            widget.clicked.connect(
                lambda state, instance=full_value.split('/')[1]:
                self.symbol.setText(instance))
            widget.clicked.connect(
                lambda state, instance=full_value:
                self.string_to_set.setText(instance))
            widget.clicked.connect(
                lambda: self.set_ok_enabled())

            if iconset == full_value.split('/')[0]:
                self.icons_dict[iconset].append(widget)
            else:
                iconset = full_value.split('/')[0]
                self.icons_dict.update({iconset: []})
                self.icons_dict[iconset].append(widget)

            widget.setIcon(QtGui.QIcon(os.path.join(self.icons_path,
                                                    full_value+'.png')))
            widget.setIconSize(QSize(30, 30))
            widget.setFixedSize(32, 32)

    def change_icon(self, gtask, code_dict, flag_list, code_dict_changer,
                    code_string_changer):
        """
        change icon and text of principal button and call the change_command
        """

        if self.symbol.text():
            self.widget.setIcon(QtGui.QIcon(os.path.join(
                str(self.icons_path), str(self.string_to_set.text())+'.png')))
            self.widget.setText(self.string_to_set.text())
            del self.string_to_set
            self.change_command(gtask, flag_list, self.widget,
                                code_dict_changer, code_string_changer)

    def set_ok_enabled(self):
        """
        change the OK button to enabled if you have chosen an icon
        """

        if self.ok.isEnabled() is False:
            self.ok.setEnabled(True)


class Quiet(QtGui.QWidget):
    """
    widget with which user can choose quiet, normal or verbose module output
    """
    def __init__(self, gtask, code_dict, flag_list, code_dict_changer,
                 code_string_changer):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        super(Quiet, self).__init__()
        self.setLayout(self.get_layout(gtask, flag_list, code_dict_changer,
                                       code_string_changer))

    def get_layout(self, gtask, flag_list, code_dict_changer,
                   code_string_changer):
        """
        create slider and wrap it into a layout
        :return: completed layout
        """

        label = QtGui.QLabel('Normal module output')
        slider = QtGui.QSlider(Qt.Horizontal)
        slider.setSingleStep(1)
        slider.setMinimum(0)
        slider.setMaximum(2)
        slider.setValue(1)
        slider.setFixedWidth(slider.sizeHint().width())

        slider.valueChanged.connect(lambda: self.slider_moved(slider, label))
        slider.valueChanged.connect(lambda: self.change_command(
            gtask, flag_list, label, code_dict_changer, code_string_changer))

        layout = QtGui.QHBoxLayout()
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(slider)

        return layout

    def slider_moved(self, slider, label):
        """
        change label when slider moves
        :param slider: the main widget
        :param label: label telling user which output does he have chosen
        """
        if slider.value() == 1:
            label.setText('Normal module output')
        elif slider.value() == 0:
            label.setText('Quiet module output')
        else:
            label.setText('Verbose module output')
