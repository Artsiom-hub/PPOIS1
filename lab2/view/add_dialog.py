
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton

class AddStudentDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добавить студента")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ФИО")

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Группа")

        self.activities_input = QLineEdit()
        self.activities_input.setPlaceholderText("10 чисел через пробел")

        self.submit_btn = QPushButton("Добавить")

        layout.addWidget(self.name_input)
        layout.addWidget(self.group_input)
        layout.addWidget(self.activities_input)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)