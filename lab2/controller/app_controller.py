
from tkinter import dialog
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWidgets import QApplication, QMessageBox
from model.storage import StudentStorage
from model.student import Student
from view.main_window import MainWindow
from view.add_dialog import AddStudentDialog
from view.search_dialog import SearchDialog
from view.delete_dialog import DeleteDialog

class AppController:
    def __init__(self):

        self.app = QApplication([])
        self.model = StudentStorage()
        self.view = MainWindow()
        self.view.update_table(self.model.get_all())
        self.view.update_tree(self.model.get_all())
        self.view.table_view_action.triggered.connect(self.view.show_table)
        self.view.tree_view_action.triggered.connect(self.view.show_tree)
        self.view.search_action.triggered.connect(self.open_search_dialog)
        self.view.delete_action.triggered.connect(self.open_delete_dialog)
        self.view.save_xml_action.triggered.connect(self.save_xml)
        self.view.load_xml_action.triggered.connect(self.load_xml)
        
        self.view.add_action.triggered.connect(self.open_add_dialog)
    def save_xml(self):
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Сохранить XML", "", "XML Files (*.xml)"
        )

        if path:
            self.model.save_to_xml(path)


    def load_xml(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Загрузить XML", "", "XML Files (*.xml)"
        )

        if path:
            self.model.load_from_xml(path)

            data = self.model.get_all()
            self.view.update_table(data)
            self.view.update_tree(data)
    def open_add_dialog(self):
        dialog = AddStudentDialog()

        def handle_submit():
            name = dialog.name_input.text()
            group = dialog.group_input.text()
            activities = list(map(int, dialog.activities_input.text().split()))

            student = Student(name, group, activities)
            self.model.add(student)

            self.view.update_table(self.model.get_all())
            self.view.update_tree(self.model.get_all())
            dialog.accept()

        dialog.submit_btn.clicked.connect(handle_submit)
        dialog.exec()
    def open_search_dialog(self):
        dialog = SearchDialog()

        def handle_search():
            print("CLICKED") 
            name = dialog.name_input.text() or None
            group = dialog.group_input.text() or None

            min_val = dialog.min_input.text()
            max_val = dialog.max_input.text()

            print("RAW:", min_val, max_val)  
            min_val = int(min_val) if min_val else None
            max_val = int(max_val) if max_val else None
            print("PARSED:", min_val, max_val)  
            results = self.model.search(name, group, min_val, max_val)
            print("RESULTS:", results)
            dialog.update_results(results)
    

        dialog.search_btn.clicked.connect(handle_search)
        dialog.exec()
        from view.delete_dialog import DeleteDialog




    def _parse_int(self, text: str):
        text = text.strip()
        return int(text) if text.isdigit() else None


    def open_delete_dialog(self):
        dialog = DeleteDialog()

        def collect_inputs():
            name = dialog.name_input.text() or None
            group = dialog.group_input.text() or None
            min_val = self._parse_int(dialog.min_input.text())
            max_val = self._parse_int(dialog.max_input.text())
            return name, group, min_val, max_val

        
        def handle_preview():
            name, group, min_val, max_val = collect_inputs()
            candidates = self.model.search(name, group, min_val, max_val)
            dialog.update_results(candidates)

        
        def handle_delete():
            name, group, min_val, max_val = collect_inputs()

            
            if not any([name, group, min_val is not None, max_val is not None]):
                QMessageBox.warning(
                    dialog,
                    "Удаление",
                    "Задайте хотя бы одно условие удаления."
                )
                return

            
            confirm = QMessageBox.question(
                dialog,
                "Подтверждение удаления",
                "Удалить записи по заданным условиям?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

            removed = self.model.delete(name, group, min_val, max_val)

            
            self.view.update_table(self.model.get_all())
            self.view.update_tree(self.model.get_all())

            
            dialog.update_results([])

       
            if removed > 0:
                QMessageBox.information(
                    dialog,
                    "Удаление выполнено",
                    f"Удалено записей: {removed}"
                )
            else:
                QMessageBox.information(
                    dialog,
                    "Удаление",
                    "Записей по заданным условиям не найдено."
                )

        dialog.preview_btn.clicked.connect(handle_preview)
        dialog.delete_btn.clicked.connect(handle_delete)

        dialog.exec()
    def run(self):
        self.view.show()
        self.app.exec()