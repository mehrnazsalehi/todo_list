from IPython.external.qt_for_kernel import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QCalendarWidget, QLabel, QLineEdit, QPushButton, \
    QListWidgetItem, QMessageBox, QListWidget
from PyQt5 import uic
import sys
import sqlite3

# Create a database or connect to one
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# Create a table
'''cursor.execute("""CREATE TABLE if not exists tasks(
    task text,
    completed text,
    date text)
    """)'''


class TodoList(QMainWindow):
    def __init__(self):
        super(TodoList, self).__init__()

        uic.loadUi("todo_list.ui", self)

        # Define our widgets
        self.calendar = self.findChild(QCalendarWidget, "calendarWidget")
        self.label = self.findChild(QLabel, "label")
        self.addTaskButton = self.findChild(QPushButton, "addButton")
        self.listItem = self.findChild(QListWidgetItem, "tasklistWidget")
        self.tasklistWidget = self.findChild(QListWidget, "tasklistWidget")
        self.tasklistWidget_view = self.findChild(QListWidget, "tasklistWidget_view")
        self.saveButton = self.findChild(QPushButton, "saveButton")
        self.doneTaskButton = self.findChild(QPushButton, "doneTaskButton")
        self.calendarWidget.selectionChanged.connect(self.calendar_date_changed)
        self.calendar_date_changed()

        self.addTaskButton.clicked.connect(self.addTaskWindow)
        self.doneTaskButton.clicked.connect(self.done)

        self.saveButton.clicked.connect(self.saveChanges)

    # change calendar date
    def calendar_date_changed(self):
        date_selected = self.calendarWidget.selectedDate().toPyDate()
        self.update_task_list(date_selected)

    def addTaskWindow(self):
        add_task = AddTaskWindow()
        widget.addWidget(add_task)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def update_task_list(self, date):
        self.tasklistWidget.clear()
        self.tasklistWidget_view.clear()

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        query = "SELECT task, completed FROM tasks WHERE date = ?"
        row = (date,)
        results = cursor.execute(query, row).fetchall()
        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasklistWidget.addItem(item)

        for result in results:
            item = QListWidgetItem(str(result[0]))
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            if result[1] == "YES":
                item.setCheckState(QtCore.Qt.Checked)
            elif result[1] == "NO":
                item.setCheckState(QtCore.Qt.Unchecked)
            self.tasklistWidget_view.addItem(item)

    def saveChanges(self):
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        date = self.calendarWidget.selectedDate().toPyDate()

        for i in range(self.tasklistWidget.count()):
            item = self.tasklistWidget.item(i)
            task = item.text()
            if item.checkState() == QtCore.Qt.Checked:
                query = "UPDATE tasks SET completed = 'YES' WHERE task = ? AND date = ?"
            else:
                query = "UPDATE tasks SET completed = 'NO' WHERE task = ? AND date = ?"
            row = (task, date,)
            cursor.execute(query, row)
        conn.commit()

        messageBox = QMessageBox()
        messageBox.setText("Changes saved.")
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.exec()

    def done(self):

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks;', )
        conn.commit()
        conn.close()

        self.tasklistWidget_view.clear()
        self.tasklistWidget.clear()


class AddTaskWindow(QMainWindow):
    def __init__(self):
        super(AddTaskWindow, self).__init__()

        uic.loadUi("add_task.ui", self)
        self.todoList = todoList

        # Define our widgets
        self.doneButton = self.findChild(QPushButton, "doneButton")
        self.lineEdit = self.findChild(QLineEdit, "lineEdit")

        self.doneButton.clicked.connect(self.addNewTask)

    def addNewTask(self):

        self.todoList.label.hide()

        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        newTask = str(self.lineEdit.text())

        date = self.todoList.calendarWidget.selectedDate().toPyDate()

        query = "INSERT INTO tasks(task, completed, date) VALUES (?,?,?)"
        row = (newTask, "NO", date,)

        cursor.execute(query, row)
        conn.commit()
        self.todoList.update_task_list(date)
        self.lineEdit.clear()

        widget.addWidget(todoList)
        widget.setCurrentIndex(widget.currentIndex() + 1)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    todoList = TodoList()
    add_task = AddTaskWindow()
    widget.addWidget(todoList)
    widget.addWidget(add_task)
    widget.setFixedHeight(558)
    widget.setFixedWidth(472)
    widget.show()
    app.exec_()
