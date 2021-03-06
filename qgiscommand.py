import sys
import os

from string import Template
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerPython

import command
import qgis_commands
import layer_commands
import package_commands

_start_prompt = "> "
_ui_settings = {
    "Background": '#36454f',
    "Font_Color": 'white',
    "Header_Background": '#5c8f0f'
}


class Notify(QObject):
    settingChanged = pyqtSignal()

notify = Notify()


class SourceViewer(QsciScintilla):
    def __init__(self, syntax='Python', parent=None):
        super(SourceViewer, self).__init__(parent)
        if syntax == 'Python':
            self.lex = QsciLexerPython(self)
            self.setLexer(self.lex)
        self.setReadOnly(True)

    def setText(self, text, line=0):
        super(SourceViewer, self).setText(text)
        self.setFirstVisibleLine(line)


def show_viewer(text, lineno=0, title='', syntax='Python'):
    dlg = QDialog()
    dlg.setWindowTitle(title)
    dlg.setLayout(QGridLayout())
    dlg.layout().setContentsMargins(0, 0, 0, 0)
    view = SourceViewer(syntax)
    dlg.layout().addWidget(view)
    view.setText(text, lineno)
    view.resize(500, 500)
    dlg.exec_()


@command.command()
def help():
    """
    Show home page for the command bar
    """
    QDesktopServices.openUrl(QUrl("http://qgiscommand.readthedocs.org/en/latest/"))


@command.command("Prompt?")
def set_commandbar_prompt(char):
    global _start_prompt
    _start_prompt = "{} ".format(char)


@command.complete_name("UI Items")
def list_ui_items(argname, data):
    return _ui_settings.keys()


@command.command("Item?", "Hex color for background?")
@command.complete_with(item=list_ui_items)
def set_commandbar_color(item, color):
    _ui_settings[item] = color
    notify.settingChanged.emit()


@command.command("Command name")
@command.check(name=command.is_comamnd)
@command.complete_with(name=command.commandlist)
def command_help(name):
    """
    Lookup the help for a given command
    """
    helptext = command.help_text[name]
    show_viewer(helptext, title="Help for {}".format(name), syntax='')


@command.command("Command name")
@command.check(name=command.is_comamnd)
@command.complete_with(name=command.commandlist)
def view_source(name):
    """
    Lookup the source code for a given command
    """
    func = command.commands[name]
    filename, lineno = command.sourcelookup[name]
    with open(filename, "r") as f:
        source = f.read()
    show_viewer(source, lineno, filename)


class CompletionModel(QStandardItemModel):
    def __init__(self, items=None, parent=None):
        super(CompletionModel, self).__init__(parent)
        self.filtermodel = QSortFilterProxyModel()
        self.filtermodel.setSourceModel(self)

        if not items:
            items = []
        self.add_entries(items)

    def add_entry(self, data, helptext):
        data = u"{}".format(unicode(data))
        item = QStandardItem(data)
        item.setData(helptext, Qt.UserRole + 1)
        self.appendRow(item)

    def add_entries(self, entries):
        for entry in entries:
            if isinstance(entry, tuple):
                data, helptext = entry[0], entry[1]
            else:
                data, helptext = entry, ''

            self.add_entry(data, helptext)

    def set_filter(self, userdata):
        fuzzy = "".join(["{}.*".format(c) for c in userdata])
        self.filtermodel.setFilterRegExp(fuzzy)
        index = self.filtermodel.index(0, 0)
        return index

    @property
    def filtered_item_count(self):
        return self.filtermodel.rowCount()

    def filtered_item_data(self, index):
        if index.isValid():
            return self.filtermodel.data(index)
        else:
            return None


class CompletionView(QWidget):
    completeRequest = pyqtSignal()

    def __init__(self, mainwindow, completions=None, parent=None):
        super(CompletionView, self).__init__(parent)
        self.mainwindow = mainwindow
        self.autocompletemodel = CompletionModel(completions)
        self.autocompleteview = QListView(self)
        self.autocompleteview.setModel(self.autocompletemodel.filtermodel)
        self.setWindowFlags(Qt.Popup)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFocusProxy(self)
        self.autocompleteview.setMouseTracking(True)
        self.autocompleteview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.autocompleteview.installEventFilter(self)
        self.selectionmodel = self.autocompleteview.selectionModel()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.headerlabel = QLabel(self)
        self.headerlabel.setText("Commands")
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().addWidget(self.headerlabel)
        self.layout().addWidget(self.autocompleteview)
        notify.settingChanged.connect(self.update_ui)
        self.styletemplate = Template("""
            QLabel { font: bold 12pt; color: ${Font_Color} ; background-color: ${Header_Background} }
            QListView:item:selected { color: #36454f; background: #7abd14 }
            QListView:item { color: ${Font_Color}  }
            QListView {background-color: $Background; border: none; }""")
        self.update_ui()

    def update_ui(self):
        style = self.styletemplate.safe_substitute(_ui_settings)
        self.setStyleSheet(style)

    def move_down(self):
        index = self.autocompleteview.currentIndex()
        row = index.row() + 1
        newindex = self.autocompletemodel.filtermodel.index(row, 0)
        if newindex.isValid():
            self.autocompleteview.setCurrentIndex(newindex)

    def move_up(self):
        index = self.autocompleteview.currentIndex()
        row = index.row() - 1
        newindex = self.autocompletemodel.filtermodel.index(row, 0)
        if newindex.isValid():
            self.autocompleteview.setCurrentIndex(newindex)

    def eventFilter(self, obj, event):
        # WAT!? If this isn't here then the plugin crashes on unload
        if not QEvent:
            return False

        if event.type() == QEvent.MouseButtonPress:
            self.parent().setFocus()
            return True

        if event.type() == QEvent.KeyPress:
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_N:
                self.move_down()
            if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
                self.move_up()
            if event.key() in [Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Return]:
                self.completeRequest.emit()
                self.hide()
                self.parent().setFocus()
                return True
            if event.key() in [Qt.Key_Up, Qt.Key_Down]:
                return False
            else:
                self.parent().setFocus()
                self.parent().event(event)

        return False

    def filter_autocomplete(self, userdata):
        index = self.autocompletemodel.set_filter(userdata)
        if index.isValid():
            self.selectionmodel.clear()
            self.selectionmodel.select(index, QItemSelectionModel.SelectCurrent)
            self.autocompleteview.scrollTo(index,
                                           QAbstractItemView.EnsureVisible)

            self.show_completion()

    def add_completions(self, completions, header):
        self.headerlabel.setText(header)
        self.autocompletemodel.clear()
        self.autocompletemodel.add_entries(completions)

    def show_completion(self):
        hasdata = self.autocompletemodel.filtered_item_count > 0
        size = self.mainwindow.height() / 100 * 15
        rowsize = self.autocompleteview.sizeHintForRow(0)
        newheight = self.autocompletemodel.filtered_item_count * rowsize
        if newheight < size:
            size = newheight + rowsize
        self.resize(self.parent().width(), size)
        self.move(self.parent().mapToGlobal(QPoint(0, 0 - self.height())))
        self.autocompleteview.setFocus()
        self.setVisible(hasdata)

    @property
    def selected_completion(self):
        try:
            index = self.autocompleteview.selectedIndexes()[0]
        except IndexError:
            return None

        text = self.autocompletemodel.filtered_item_data(index)
        return text


class CommandShell(QLineEdit):
    def __init__(self, mainwindow, parent=None):
        super(CommandShell, self).__init__(parent)
        self.mainwindow = mainwindow
        self.settings = QSettings()
        self.prompt = _start_prompt
        self.currentfunction = None
        self.textChanged.connect(self.text_changed)
        self.autocompleteview = CompletionView(self.mainwindow, parent=self)
        self.autocompleteview.completeRequest.connect(self.complete)
        self.show_prompt()
        notify.settingChanged.connect(self.update_ui)
        self.styletemplate = Template("""
                    QLineEdit { border: none; background: $Background; color: ${Font_Color}  }""")
        self.update_ui()

    def update_ui(self):
        style = self.styletemplate.safe_substitute(_ui_settings)
        self.setStyleSheet(style)

    def text_changed(self):
        userdata = self.get_data()
        if not self.currentfunction:
            completions, userdata, header = command.completions_for_line(self.get_data())
            self.autocompleteview.add_completions(completions, header)
        self.autocompleteview.filter_autocomplete(userdata)

    def finsihed(self):
        self.parent().removeEventFilter(self)

    def event(self, event):
        if not QEvent:
            return False

        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.complete()
            return True

        return super(CommandShell, self).event(event)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.entered()
        elif e.key() == Qt.Key_Escape:
            self.end_current()
        elif e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            newindex = self.cursorPosition()
            if newindex > len(self.prompt):
                super(CommandShell, self).keyPressEvent(e)
        else:
            super(CommandShell, self).keyPressEvent(e)

    def complete(self):
        text = self.autocompleteview.selected_completion
        if not text:
            return False
        # Wrap text with space in quotes
        if ' ' in text and not self.currentfunction:
            # TODO Handle escaping better
            text = "'{}'".format(text)

        line = self.get_data()
        space = line.rfind(' ')
        newline = line[:space + 1] + text + " "
        self.show_prompt(self.prompt, newline)
        return True

    def end_current(self):
        self.currentfunction = None
        self.show_prompt()

    def show_prompt(self, prompt=None, data=None):
        self.clear()
        if not prompt:
            prompt = _start_prompt

        if not prompt == _start_prompt:
            prompt += ":"

        text = prompt

        if data:
            text = prompt + str(data)

        self.setText(text)
        self.prompt = prompt
        self.move_cursor_to_end()

    def get_end_pos(self):
        """Return (line, index) position of the last character"""
        return len(self.text())

    def move_cursor_to_end(self):
        """Move cursor to end of text"""
        self.end(False)

    def get_data(self):
        line = self.text()
        line = line[len(self.prompt):]
        return line


    def run_line(self, line):
        if not line:
            return

        if not self.currentfunction:
            try:
                gen = command.parse_line_data(line)
            except command.NoFunction:
                return

            if gen:
                self.currentfunction = gen
                line = None
            else:
                self.currentfunction = None
                self.show_prompt()
                return

        try:
            prompt, data, completions = self.currentfunction.send(line)
            completions, header = completions[0], completions[1]
            self.show_prompt(prompt, data)
            self.autocompleteview.add_completions(completions, header)
            self.autocompleteview.filter_autocomplete("")
        except StopIteration:
            self.currentfunction = None
            self.show_prompt()
        except command.NoFunction:
            self.currentfunction = None

    def show_completion(self):
        self.autocompleteview.show_completion()

    def entered(self):
        line = self.get_data()
        self.run_line(line)

    def set_settings(self):
        loadFont = self.settings.value("pythonConsole/fontfamilytext",
                                       "Monospace")
        fontSize = self.settings.value("pythonConsole/fontsize", 10, type=int)

        font = QFont(loadFont)
        font.setFixedPitch(True)
        font.setPointSize(fontSize)
        font.setStyleHint(QFont.TypeWriter)
        font.setStretch(QFont.SemiCondensed)
        font.setLetterSpacing(QFont.PercentageSpacing, 87.0)
        font.setBold(False)

        self.setFont(font)

    def activated(self):
        visible = self.isVisible()
        self.setVisible(not visible)


if __name__ == "__main__":
    c = CommandShell(iface.mapCanvas())
    c.activated()
