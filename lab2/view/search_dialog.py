# view/search_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem
)


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поиск")

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Фамилия")

        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Группа")

        self.min_input = QLineEdit()
        self.min_input.setPlaceholderText("Мин")

        self.max_input = QLineEdit()
        self.max_input.setPlaceholderText("Макс")

        self.search_btn = QPushButton("Найти")

        # 🔥 Таблица результатов (ключевая часть ТЗ)
        self.result_table = QTableWidget(0, 12)
        self.result_table.setHorizontalHeaderLabels(
            ["ФИО", "Группа"] + [f"{i} сем" for i in range(1, 11)]
        )

        layout.addWidget(QLabel("Поиск"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.group_input)
        layout.addWidget(self.min_input)
        layout.addWidget(self.max_input)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.result_table)

        self.setLayout(layout)

    def update_results(self, students):
        self.result_table.setRowCount(len(students))

        for row, s in enumerate(students):
            self.result_table.setItem(row, 0, QTableWidgetItem(s.full_name))
            self.result_table.setItem(row, 1, QTableWidgetItem(s.group))

            for i, val in enumerate(s.activities):
                self.result_table.setItem(row, i + 2, QTableWidgetItem(str(val)))
