# view/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QToolBar,  QMenuBar, QTreeWidget, QTreeWidgetItem, QStackedWidget, 
    QPushButton, QLabel, QHBoxLayout, QSpinBox, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QAction

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.page_size = 10
        self.current_data = []
        central_widget = QWidget()
        
        self.setCentralWidget(central_widget)
        
        self.setWindowTitle("Студенты")

        # Таблица
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels(
            ["ФИО", "Группа"] + [f"{i} сем" for i in range(1, 11)]
        )
        # таблица (оставь как есть)
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels(
            ["ФИО", "Группа"] + [f"{i} сем" for i in range(1, 11)]
        )
        pagination_layout = QHBoxLayout()

        self.first_btn = QPushButton("<<")
        self.prev_btn = QPushButton("<")
        self.next_btn = QPushButton(">")
        self.last_btn = QPushButton(">>")

        self.page_label = QLabel("Страница 1 / 1")

        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(1, 100)
        self.page_size_spin.setValue(10)

        self.total_label = QLabel("Всего: 0")

        pagination_layout.addWidget(self.first_btn)
        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.next_btn)
        pagination_layout.addWidget(self.last_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(QLabel("На странице:"))
        pagination_layout.addWidget(self.page_size_spin)
        pagination_layout.addWidget(self.total_label)

        self.first_btn.clicked.connect(self.go_first)
        self.prev_btn.clicked.connect(self.go_prev)
        self.next_btn.clicked.connect(self.go_next)
        self.last_btn.clicked.connect(self.go_last)
        self.page_size_spin.valueChanged.connect(self.change_page_size)
        

        # 🔥 контейнер (переключение)
        self.stack = QStackedWidget()

        # 🔥 дерево
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Данные"])

        self.stack.addWidget(self.table)
        self.stack.addWidget(self.tree)

        # 🔥 главный layout
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        layout.addLayout(pagination_layout)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
      

       

   

        # Меню
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")


        

        # Toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        self.add_action = QAction("Добавить", self)
        self.search_action = QAction("Поиск", self)
        self.delete_action = QAction("Удалить", self)
        self.table_view_action = QAction("Таблица", self)
        self.tree_view_action = QAction("Дерево", self)
        self.save_xml_action = QAction("Сохранить XML", self)
        self.load_xml_action = QAction("Загрузить XML", self)

        file_menu.addAction(self.save_xml_action)
        file_menu.addAction(self.load_xml_action)
        file_menu.addAction(self.table_view_action)
        file_menu.addAction(self.tree_view_action)
        file_menu.addAction(self.delete_action)
        file_menu.addAction(self.search_action)
        file_menu.addAction(self.add_action)
        
        toolbar.addAction(self.table_view_action)
        toolbar.addAction(self.tree_view_action)
        toolbar.addAction(self.delete_action)
        toolbar.addAction(self.search_action)
        toolbar.addAction(self.add_action)
        toolbar.addAction(self.save_xml_action)
        toolbar.addAction(self.load_xml_action)
    def go_first(self):
        self.current_page = 1
        self._render_page()

    def go_prev(self):
        if self.current_page > 1:
            self.current_page -= 1
        self._render_page()

    def go_next(self):
        total = len(self.current_data)
        total_pages = max(1, (total + self.page_size - 1) // self.page_size)

        if self.current_page < total_pages:
            self.current_page += 1
        self._render_page()

    def go_last(self):
        total = len(self.current_data)
        self.current_page = max(1, (total + self.page_size - 1) // self.page_size)
        self._render_page()

    def change_page_size(self, value):
        self.page_size = value
        self.current_page = 1
        self._render_page()
    def _render_page(self):
        total = len(self.current_data)
        page_size = self.page_size
        total_pages = max(1, (total + page_size - 1) // page_size)

        # фикс выхода за границы
        if self.current_page > total_pages:
            self.current_page = total_pages

        start = (self.current_page - 1) * page_size
        end = start + page_size
        page_data = self.current_data[start:end]

        # заполняем таблицу
        self.table.setRowCount(len(page_data))

        for row, s in enumerate(page_data):
            self.table.setItem(row, 0, QTableWidgetItem(s.full_name))
            self.table.setItem(row, 1, QTableWidgetItem(s.group))

            for i, val in enumerate(s.activities):
                self.table.setItem(row, i + 2, QTableWidgetItem(str(val)))

        # обновляем UI
        self.page_label.setText(f"Страница {self.current_page} / {total_pages}")
        self.total_label.setText(f"Всего: {total}")
    def update_table(self, students):
        self.current_data = students
        self.current_page = 1
        self._render_page()
    def show_table(self):
        self.stack.setCurrentIndex(0)

    def show_tree(self):
        self.stack.setCurrentIndex(1)
    def _get_page_data(self, students):
        total = len(students)
        page_size = self.page_size
        total_pages = max(1, (total + page_size - 1) // page_size)

        if self.current_page > total_pages:
            self.current_page = total_pages

        start = (self.current_page - 1) * page_size
        end = start + page_size

        return students[start:end]    
    def update_tree(self, students):
        students = self._get_page_data(students)
        self.tree.clear()

        for s in students:
            root = QTreeWidgetItem([s.full_name])  # имя как корень

            root.addChild(QTreeWidgetItem([f"Группа: {s.group}"]))

            for i, val in enumerate(s.activities, start=1):
                root.addChild(QTreeWidgetItem([f"{i} сем: {val}"]))

            self.tree.addTopLevelItem(root)

        self.tree.expandAll()