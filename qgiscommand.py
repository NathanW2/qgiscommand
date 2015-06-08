import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerCustom, QsciAPIs, QsciLexerPython

import command
import qgis_commands
import layer_commands

_start_prompt = "> "

import logger

# logger.msg('Test message from qgiscommand.py')


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
    Show help for the command bar
    """
    # TODO Replace this with a html page for help
    helptext = """Command Bar help

To get help on a command type: command-help
Current commands:
{commands}
    """.format(commands="\n".join(command.commands.keys()))
    name = "Command bar"
    show_viewer(helptext, title="Help for {}".format(name), syntax='')


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



class CommandShell(QLineEdit):
    def __init__(self, parent=None):
        super(CommandShell, self).__init__(parent)
        self.settings = QSettings()
        self.lex = QsciLexerPython(self)
        self.apis = QsciAPIs(self.lex)
        self.lex.setAPIs(self.apis)
        self._start_prompt = _start_prompt
        self.prompt = self._start_prompt
        self.currentfunction = None
        self.textChanged.connect(self.text_changed)
        self._lastcompletions = None
        self.autocompletemodel = QStandardItemModel()
        self.autocompletefilter = QSortFilterProxyModel()
        self.autocompletefilter.setSourceModel(self.autocompletemodel)
        self.autocompleteview = QListView(self.parent())
        self.autocompleteview.setStyleSheet("""
            QListView:item:selected { color: #111513; background: white }
            QListView:item { color: white }
            QListView {background-color: #111513 }""")
        self.autocompleteview.setModel(self.autocompletefilter)
        self.autocompleteview.setWindowFlags(Qt.Popup)
        self.autocompleteview.setFocusPolicy(Qt.NoFocus)
        self.autocompleteview.setFocusProxy(self)
        self.autocompleteview.setMouseTracking(True)
        self.autocompleteview.hide()
        self.setStyleSheet("QLineEdit { background: #111513; color: white }")
        self.selectionmodel = self.autocompleteview.selectionModel()
        self.autocompleteview.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.autocompleteview.installEventFilter(self)
        self.show_prompt()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.autocompleteview.hide()
            self.setFocus()
            return True

        if event.type() == QEvent.KeyPress:
            if event.key() in [Qt.Key_Tab, Qt.Key_Enter, Qt.Key_Return]:
                self.complete()
                self.autocompleteview.hide()
                self.setFocus()
                self.event(event)
                return True
            if event.key() in [Qt.Key_Up, Qt.Key_Down]:
                return False
            else:
                self.setFocus()
                self.event(event)

        return False

    def show_completion(self):
        self.autocompleteview.setVisible(False)
        hasdata = self.autocompletemodel.rowCount() > 0
        self.autocompleteview.adjustSize()
        self.autocompleteview.resize(self.width(), 150)
        self.autocompleteview.move(self.mapToGlobal(QPoint(0, 0 - self.autocompleteview.height())))
        self.autocompleteview.setFocus()
        self.autocompleteview.setVisible(hasdata)

    def add_completions(self, completions):
        self.autocompletemodel.clear()
        for value in completions:
            data = u"{}".format(unicode(value))
            self.autocompletemodel.appendRow(QStandardItem(data))

    def filter_autocomplete(self, userdata, filteronly=False):
        fuzzy = "".join(["{}.*".format(c) for c in userdata])
        self.autocompletefilter.setFilterRegExp(fuzzy)
        index = self.autocompletefilter.index(0, 0)
        if index.isValid():
            self.selectionmodel.clear()
            self.selectionmodel.select(index, QItemSelectionModel.SelectCurrent)
            self.autocompleteview.scrollTo(index,
                                           QAbstractItemView.EnsureVisible)

            self.show_completion()

    def text_changed(self):
        userdata = self.get_data()
        if not self.currentfunction:
            completions, userdata = command.completions_for_line(self.get_data())
            self.add_completions(completions)
        self.filter_autocomplete(userdata)

    def finsihed(self):
        self.parent().removeEventFilter(self)
        self.close()

    def event(self, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab:
            self.complete()
            return True

        return super(CommandShell, self).event(event)
                
    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.entered()
        elif e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            newindex = self.cursorPosition()
            if newindex > len(self.prompt):
                super(CommandShell, self).keyPressEvent(e)
        else:
            super(CommandShell, self).keyPressEvent(e)

    def complete(self):
        try:
            index = self.autocompleteview.selectedIndexes()[0]
        except IndexError:
            return False

        if index.isValid():
            text = self.autocompletefilter.data(index)
            # Wrap text with space in quotes
            if ' ' in text:
                text = "'{}'".format(text)

            line = self.get_data()
            space = line.rfind(' ')
            newline = line[:space + 1] + text + " "
            self.show_prompt(self.prompt, newline)
            return True

    def close(self):
        if self.currentfunction:
            # If there is a current function we don't kill the bar just the
            # current function
            self.currentfunction = None
            self.show_prompt()
            return
        self.currentfunction = None
        self.autocompleteview.close()
        super(CommandShell, self).close()

    def show_prompt(self, prompt=_start_prompt, data=None):
        self.clear()
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
            self.show_prompt(prompt, data)
            self.add_completions(completions)
        except StopIteration:
            self.currentfunction = None
            self.show_prompt()
        except command.NoFunction:
            self.currentfunction = None

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
