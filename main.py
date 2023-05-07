from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, \
    QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class DatabaseConnection():
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(640, 480)

        file_menu_item = self.menuBar().addMenu("&File")
        #help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        search_student = QAction(QIcon("icons/search.png"),"Search Student", self)
        search_student.triggered.connect(self.searchStudent)
        edit_menu_item.addAction(search_student)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar and add toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_student)

        # Create status bar and add status bar element

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a click

        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                 self.statusbar.removeWidget(child)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()
        self.table

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def searchStudent(self):
        dialog = SearchStudentDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
         Feel free to use it
        """
        self.setText(content)
class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update New Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get student name from selected row

        index = management_system.table.currentRow()
        student_name = management_system.table.item(index, 1).text()

        # Get  id from selected row

        self.student_id = management_system.table.item(index, 0).text()

        # Add student name
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        course_name = management_system.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        # Add mobile widget
        mobile_phone = management_system.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile_phone)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add Submit Button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name= ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh The table
        management_system.load_data()


class DeleteDialog(QDialog):
    def __init__(self):
       super().__init__()
       self.setWindowTitle("Delete Student Data")

       layout = QGridLayout()
       confirmatiom_message = QLabel("Are you sure you want to delete")
       yes = QPushButton("Yes")
       no = QPushButton("No")

       layout.addWidget(confirmatiom_message, 0, 0, 1, 2)
       layout.addWidget(yes, 1, 0)
       layout.addWidget(no, 1, 1)

       self.setLayout(layout)

       yes.clicked.connect(self.delete_student)

    def delete_student(self):
        # Get selected row and student id
        index = management_system.table.currentRow()
        student_id = management_system.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()

        self.close()
        confirmation_widget =QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()



class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insert New Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add student name
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add Submit Button
        button = QPushButton("Submit")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES(?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        management_system.load_data()

class SearchStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Search")
        self.setFixedHeight(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        self.student_search_name = QLineEdit()
        self.student_search_name.setPlaceholderText("Name")
        layout.addWidget(self.student_search_name)

        self.search_button = QPushButton("Search Student")
        self.search_button.clicked.connect(self.searchStudent)
        layout.addWidget(self.search_button)

        self.setLayout(layout)

    def searchStudent(self):
        name = self.student_search_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT *FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)
        items = management_system.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            management_system.table.item(item.row(), 1).setSelected(True)
        cursor.close()
        connection.close()


app = QApplication(sys.argv)
management_system = MainWindow()
management_system.show()
management_system.load_data()
sys.exit(app.exec())