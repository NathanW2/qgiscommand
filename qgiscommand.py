import sys
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerCustom, QsciAPIs, QsciLexerPython

import command
import qgis_commands

_start_prompt = "-> "

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


class Lexer(QsciLexerCustom):
    """
    Note: Crashes at the momemnt
    """

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)
        self._styles = {0: 'Default', 1: 'Function', }
        for key, value in self._styles.iteritems():
            setattr(self, value, key)

    def description(self, style):
        return self._styles.get(style, 'Default')

    def defaultColor(self, style):
        if style == self.Default:
            return QColor('#000000')
        elif style == self.Function:
            return QColor('#C0C0C0')
        return QsciLexerCustom.defaultColor(self, style)

    def styleText(self, start, end):
        print start, end


class CommandShell(QsciScintilla):
    def __init__(self, parent=None):
        super(CommandShell, self).__init__(parent)
        self.setMinimumHeight(50)
        self.setMaximumHeight(50)
        self.settings = QSettings()
        self.lex = QsciLexerPython(self)
        self.apis = QsciAPIs(self.lex)
        self.lex.setAPIs(self.apis)
        self.setLexers()
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.SendScintilla(QsciScintilla.SCI_SETVSCROLLBAR, 0)
        self.setFolding(0)
        self._start_prompt = _start_prompt
        self.prompt = self._start_prompt
        self.currentfunction = None
        self.setAutoCompletionSource(self.AcsAPIs)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionReplaceWord(True)
        self.setCallTipsStyle(QsciScintilla.CallTipsNoContext)
        self.parent().installEventFilter(self)
        self.textChanged.connect(self.text_changed)
        self._lastcompletions = None
        self.autocompletemodel = QStandardItemModel()
        self.autocompletefilter = QSortFilterProxyModel()
        self.autocompletefilter.setSourceModel(self.autocompletemodel)
        self.autocompleteview = QListView(self.parent())
        self.autocompleteview.setStyleSheet("QListView::item:selected {border: 1px solid black; }")
        self.autocompleteview.setModel(self.autocompletefilter)
        self.autocompleteview.hide()
        self.selectionmodel = self.autocompleteview.selectionModel()
        # command.register_command(self.run_last_command,
        #                          alias="!!",
        #                          nohistory=True)

    def adjust_auto_complete(self):
        self.autocompleteview.resize(self.parent().width(), 100)
        self.autocompleteview.move(0, self.parent().height() - self.height() -
                                   self.autocompleteview.height())

    def add_completions(self, completions):
        self.autocompletemodel.clear()
        for value in completions:
            data = u"{}".format(unicode(value))
            self.autocompletemodel.appendRow(QStandardItem(data))
        self._lastcompletions = completions

    def text_changed(self):
        completions, userdata = command.completions_for_line(self.get_data())
        if not completions == self._lastcompletions:
            self.add_completions(completions)

        fuzzy = "".join(["{}.*".format(c) for c in userdata])
        self.autocompletefilter.setFilterRegExp(fuzzy)
        index = self.autocompletefilter.index(0, 0)
        if index.isValid():
            self.selectionmodel.clear()
            self.selectionmodel.select(index, QItemSelectionModel.SelectCurrent)
            self.autocompleteview.scrollTo(index, QAbstractItemView.EnsureVisible)

        hasdata = self.autocompletemodel.rowCount() > 0

        self.adjust_auto_complete()
        self.autocompleteview.setVisible(hasdata)

    def end(self):
        self.parent().removeEventFilter(self)
        self.close()

    def eventFilter(self, object, event):
        if event.type() == QEvent.Resize:
            self.adjust_size()
        return QWidget.eventFilter(self, object, event)

    def move_autocomplete(self, amount):
        try:
            index = self.autocompleteview.selectedIndexes()[0]
        except IndexError:
            return

        row = index.row()
        row += amount
        if row > self.autocompletefilter.rowCount() - 1:
            # Wrap to top
            row = 0
        elif row < 0:
            # Wrap to bottom
            row = self.autocompletefilter.rowCount() - 1

        print row
        index = self.autocompletefilter.index(row, 0)
        print index.isValid()
        if index.isValid():
            self.selectionmodel.select(index, QItemSelectionModel.SelectCurrent)
            self.autocompleteview.scrollTo(index, QAbstractItemView.EnsureVisible)

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.entered()
        elif e.key() == Qt.Key_Escape:
            self.close()
        elif e.key() == Qt.Key_Tab:
            self.complete()
        elif e.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            _, newindex = self.getCursorPosition()
            if newindex > len(self.prompt):
                QsciScintilla.keyPressEvent(self, e)
        elif e.key() == Qt.Key_Up:
            self.move_autocomplete(-1)
        elif e.key() == Qt.Key_Down:
            self.move_autocomplete(1)
        else:
            QsciScintilla.keyPressEvent(self, e)

    def complete(self):
        try:
            index = self.autocompleteview.selectedIndexes()[0]
        except IndexError:
            return

        if index.isValid():
            text = self.autocompletefilter.data(index)
            # Wrap text with space in quotes
            if ' ' in text:
                text = "'{}'".format(text)

            line = self.get_data()
            space = line.rfind(' ')
            newline = line[:space + 1] + text + " "
            self.show_prompt(self.prompt, newline)

    def close(self):
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
        line = self.lines() - 1
        return (line, len(self.text(line)))

    def move_cursor_to_end(self):
        """Move cursor to end of text"""
        line, index = self.get_end_pos()
        self.setCursorPosition(line, index)
        self.ensureCursorVisible()
        self.ensureLineVisible(line)

    def get_data(self):
        line = self.text()
        line = line[len(self.prompt):]
        return line

    def run_last_command(self):
        """
        Runs the last command again. (Alias -> !!)
        """
        try:
            line = command.history[-1]
            self.run_line(line)
        except IndexError:
            pass

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
            prompt, data = self.currentfunction.send(line)
            self.show_prompt(prompt, data)
        except StopIteration:
            self.currentfunction = None
            self.show_prompt()
        except command.NoFunction:
            self.currentfunction = None

    def entered(self):
        line = self.get_data()
        self.run_line(line)

    def setLexers(self):
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

        self.lex.setFont(font)
        self.lex.setDefaultFont(font)
        self.setLexer(self.lex)

    def adjust_size(self):
        fm = QFontMetrics(self.font())
        self.setMaximumHeight(20)
        self.resize(self.parent().width(), 20)
        self.move(0, self.parent().height() - self.height())
        self.adjust_auto_complete()

    def showEvent(self, event):
        self.adjust_size()
        self.show_prompt()
        self.setFocus()
        self.autocompleteview.show()

    def activated(self):
        visible = self.isVisible()
        self.setVisible(not visible)


if __name__ == "__main__":
    c = CommandShell(iface.mapCanvas())
    c.activated()
