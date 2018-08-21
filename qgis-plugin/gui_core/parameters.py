"""
@package gui_core.parameters

@brief Basic layout for widgets, factory to choose which widget use,
 simple widgets

Classes:
 - :class:'Factory'
 - :class:'Parameters'
 - :class:'SqlQuery'
 - :class:'Cats'
 - :class:'Separator'
 - classes inherited from gselect.py
 - :class:'MultipleInteger'
 - :class:'SimpleInteger'
 - :class:'Flags'
 - :class:'DefaultWidget'

(C) 2016 by the GRASS Development Team

This program is free software under the GNU General Public License
(>=v2). Read the file COPYING that comes with GRASS for details.

@author Ondrej Pesek <pesej.ondrek@gmail.com>
"""

from PyQt4 import QtGui
import gselect


class Factory():
    """
    Factory to decide which widget class should be used
    """

    def __init__(self):
        """
        constructor
        creates the list of widget classes
        """

        self.classes = [
            j for (i, j) in globals().iteritems() if hasattr(j, 'can_handle')]

    def new_widget(self, gtask, code_dict, flag_list, code_dict_changer,
                   code_string_changer):
        """
        deciding which widget class should be used
        :param gtask: part of gtask for this widget
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        :return: created widget
        """

        for oneClass in self.classes:
            if oneClass.can_handle(gtask['type'], gtask['multiple'],
                                   gtask['key_desc'], gtask['prompt'],
                                   gtask['values']):
                return oneClass(gtask, code_dict, flag_list,
                                code_dict_changer, code_string_changer)
        else:
            return DefaultWidget(gtask, code_dict, flag_list,
                                 code_dict_changer,  code_string_changer)


class Parameters():
    """
    class to create layout and call factory creating the widget
    """
    def __init__(self, gtask, module, code_dict, flag_list, code_string, fact):
        """
        constructor
        :param gtask: part of gtask for this widget
        :param module: called module
        :param code_dict: dictionary of filled parameters
        :param flag_list: list of checked flags
        :param code_string: widget with code string that user can see
        :return: completed widget
        """

        self.module = module
        self.code_dict = code_dict
        self.flag_list = flag_list
        self.code_string = code_string
        self.gtask = gtask

        box_complete = self.get_layout()
        try:
            widget = Factory.new_widget(fact, gtask, code_dict, flag_list,
                                        self.code_dict_changer,
                                        self.code_string_changer)
            box_complete.addWidget(widget)

        except:
            if gtask['name'] not in ['quiet', 'verbose']:
                widget = Flags(
                    gtask, code_dict, flag_list, self.code_dict_changer,
                    self.code_string_changer)
                box_complete.addWidget(widget)
                box_complete.addStretch()
                box_complete.addWidget(QtGui.QLabel('(%s)' % gtask['name']))
            elif gtask['name'] == 'quiet':
                widget = Quiet(
                    gtask, code_dict, flag_list, self.code_dict_changer,
                    self.code_string_changer)
                box_complete.addWidget(widget)

        if gtask['label'] and gtask['description']:
            # title is in label so we can use description as help/tooltip
            widget.setToolTip(gtask['description'])

        self.completeWidget = QtGui.QWidget()
        self.completeWidget.setLayout(box_complete)

    def new_widget(self):
        """
        :return:The widget
        """

        return self.completeWidget

    def get_layout(self):
        """
        create layout/box for the widget
        :return: layout
        """

        try:
            box_header = QtGui.QHBoxLayout()

            if self.gtask['multiple'] is True:
                box_header.addWidget(QtGui.QLabel('[multiple]'))
            if self.gtask['label']:
                description = QtGui.QLabel(self.gtask['label'] + ':')
            else:
                description = QtGui.QLabel(self.gtask['description'] + ':')

            # description.setWordWrap(True)
            box_header.addWidget(description)

            if self.gtask['required'] is True:
                star = QtGui.QLabel('*')
                star.setStyleSheet('color: red')
                box_header.addWidget(star)

            box_header.addStretch()
            if self.gtask['key_desc']:
                box_header.addWidget(QtGui.QLabel('(%s=%s)' % (
                    self.gtask['name'], self.gtask['key_desc'][0])))
            else:
                box_header.addWidget(QtGui.QLabel('(%s=%s)' % (
                    self.gtask['name'], self.gtask['type'])))

            header = QtGui.QWidget()
            header.setLayout(box_header)

            layout_complete = QtGui.QVBoxLayout()
            layout_complete.addWidget(header)

        except:
            layout_complete = QtGui.QHBoxLayout()  # flag

        layout_complete.setSpacing(0)
        layout_complete.setMargin(0)

        return layout_complete

    def code_string_changer(self):
        """
        This method changes the code string that user can see
        """
        flags = ''
        for i in self.flag_list:
            if len(i) == 1:
                flags = flags + ' -' + i
            else:
                flags = flags + ' --' + i
        self.code_string.setText(self.module + flags+' '+' '.join(
            '{}={}'.format(key, val) for key, val in self.code_dict.items()))

    def code_dict_changer(self, text):
        """
        This method is updating the dictionary of filled parameters
        :param text: text from widget which is calling this method
        """
        if text and (text != self.gtask['default'] or
                     self.gtask['name'] == 'layer'):
            try:
                self.code_dict[self.gtask['name']] = text
            except:  # it means that there is no item for this widget in dict
                self.code_dict.update({self.gtask['name']: text})
        else:
            try:
                del self.code_dict[self.gtask['name']]
                # because we don't want to have not necessary items in dict
            except:
                pass

        self.code_string_changer()


# now string types
class SqlQuery(QtGui.QLineEdit):
    """
    widget for SQL queries
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

        super(SqlQuery, self).__init__()

        if gtask['default']:
            self.setText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        """
        Tell which types of widgets is this class used for
        :param type: type of widget (string, float... )
        :param multiple: True or False (multiple or simple)
        :param key_desc: key description of widget
        :param prompt: telling information about which widget is ideal
        :param values: if there is some list of default values
        :return: Conditions for this class usage
        """
        return key_desc == ['sql_query']

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        """
        calling methods updating code_dict and code_string
        :param gtask: part of gtask for this widget
        :param flag_list: list of checked flags
        :param widget: widget from which should be read text
        :param code_dict_changer: method for changing code_dict
        :param code_string_changer: method for changing string with code
        """
        code_dict_changer(str(widget.text()))


# maybe in future implement special widget when called from gui
class Cats(QtGui.QLineEdit):
    """
    widget for category values
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

        super(Cats, self).__init__()

        if gtask['default']:
            self.setText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return prompt == 'cats'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.text()))


class Separator(QtGui.QComboBox):
    """
    widget for choosing which separator was used
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

        super(Separator, self).__init__()

        self.setEditable(True)
        self.addItems(self.get_items(gtask))

        if gtask['default']:
            self.setEditText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_items(self, gtask):
        items_string = gtask['description'].split('Special characters: ')[1]
        return items_string.split(', ')

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and prompt == 'separator'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


# inherited from gselect.py
class TreeComboBox(gselect.TreeComboBox):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'string' and key_desc != ['sql_query'] \
               and prompt in ['raster', 'vector', 'raster_3d', 'group']

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class BrowseFile(gselect.BrowseFile):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'string' and key_desc != ['sql_query'] \
               and prompt in ['file', 'dbase']

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.text()))


class MultipleValues(gselect.MultipleValues):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and (multiple is True) and values

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        value = ''
        items = (widget.itemAt(i).widget() for i in range(widget.count()-1))

        for item in items:
            if item.isChecked():
                if value:
                    value = ','.join((value, str(item.objectName())))
                else:
                    value = str(item.objectName())

        code_dict_changer(str(value))


class Layers(gselect.Layers):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and prompt == 'layer'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class Columns(gselect.Columns):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and prompt == 'dbcolumn'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class Colors(gselect.Colors):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and prompt == 'color'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        items = list((widget.itemAt(i).widget()
                      for i in range(widget.count()-1)))

        if len(items) > 1:
            if items[1].isChecked() is False:
                if str(items[0].text()) != 'Select color':
                    code_dict_changer(str(items[0].text()))
            else:
                code_dict_changer('')
        else:
            code_dict_changer(str(items[0].text()))


class DbTable(gselect.DbTable):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return prompt == 'dbtable'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class Mapsets(gselect.Mapsets):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return prompt == 'mapset'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class Locations(gselect.Locations):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return prompt == 'location'

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.currentText()))


class SimpleValues(gselect.SimpleValues):
    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return (type == 'string') and (multiple is False) and values

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        if gtask['name'] != 'icon':
            code_dict_changer(str(widget.currentText()))
        else:
            code_dict_changer(str(widget.text()))


class Quiet(gselect.Quiet):
    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        try:
            flag_list.remove('quiet')
        except:
            try:
                flag_list.remove('verbose')
            except:
                pass

        if widget.text() == 'Quiet module output':
            flag_list.append('quiet')
        elif widget.text() == 'Verbose module output':
            flag_list.append('verbose')

        code_string_changer()


# now float types
class MultipleFloat(QtGui.QLineEdit):
    """
    widget for typing float numbers (user can type in more than one number)
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

        super(MultipleFloat, self).__init__()

        if gtask['default']:
            self.setText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'float' and ((multiple is True) or prompt == 'coords')

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.text()))


class SimpleFloat(QtGui.QDoubleSpinBox):
    """
    widget for typing float number (just one, user can choose from spinbox)
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

        super(SimpleFloat, self).__init__()

        self.setRange(-10000000, 10000000)
        self.setDecimals(5)
        if gtask['default']:
            self.setValue(float(gtask['default']))

        self.valueChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'float' and multiple is False

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.value()))


# now integer types
class MultipleInteger(QtGui.QLineEdit):
    """
    widget for typing int numbers (user can type in more than one number)
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

        super(MultipleInteger, self).__init__()

        if gtask['default']:
            self.setText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'integer' and multiple is True

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.text()))


class SimpleInteger(QtGui.QSpinBox):
    """
    widget for typing int number (just one, user can choose from spinbox)
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

        super(SimpleInteger, self).__init__()

        self.setRange(-10000000, 10000000)

        if gtask['default']:
            self.setValue(int(gtask['default']))

        self.valueChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    @staticmethod
    def can_handle(type, multiple, key_desc, prompt, values):
        return type == 'integer' and multiple is False

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        code_dict_changer(str(widget.text()))


class Flags(QtGui.QCheckBox):
    """
    checkbox for flags
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

        super(Flags, self).__init__(self.get_label(gtask))

        self.stateChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def get_label(self, gtask):
        """
        deciding choose between label and dexcription
        :param gtask:
        :return: text for checkbox
        """
        if gtask['label']:
            return gtask['label']
        else:
            return gtask['description']

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):
        if widget.isChecked():
            if gtask['name'] not in flag_list:
                # it means that there is no item for this widget in dict
                flag_list.append(gtask['name'])
        else:
            flag_list.remove(gtask['name'])
            # because we don't want to have not necessary items in dict

        code_string_changer()


# default widget
class DefaultWidget(QtGui.QLineEdit):
    """
    widget for widgets those don't have any special stated
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

        super(DefaultWidget, self).__init__()

        # uncomment to highlight what should be done better
        # self.setText('TODO - Nobody expects the Spanish Inquisition')
        # palette = QtGui.QPalette()
        # palette.setColor(QtGui.QPalette.Active,
        #                  QtGui.QPalette.Base, QtGui.QColor('red'))
        # self.setPalette(palette)

        if gtask['default']:  # comment when using highlighting
            self.setText(gtask['default'])

        self.textChanged.connect(lambda: self.change_command(
            gtask, flag_list, self, code_dict_changer, code_string_changer))

    def change_command(self, gtask, flag_list, widget, code_dict_changer,
                       code_string_changer):

        code_dict_changer(str(widget.text()))
