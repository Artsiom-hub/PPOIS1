import sqlite3
from typing import List
from .student import Student
from xml.dom.minidom import Document
import xml.sax

class StudentHandler(xml.sax.ContentHandler):
        def __init__(self):
            self.students = []
            self.current_data = ""
            self.full_name = ""
            self.group = ""
            self.activities = ""

        def startElement(self, tag, attrs):
            self.current_data = tag

        def characters(self, content):
            if self.current_data == "full_name":
                self.full_name += content
            elif self.current_data == "group":
                self.group += content
            elif self.current_data == "activities":
                self.activities += content

        def endElement(self, tag):
            if tag == "student":
                activities = list(map(int, self.activities.split(",")))

                self.students.append(
                    Student(self.full_name.strip(), self.group.strip(), activities)
                )

                self.full_name = ""
                self.group = ""
                self.activities = ""
                self.current_data = ""


class StudentStorage:
    def __init__(self, db_path: str = "students.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()
    def load_from_xml(self, file_path: str):
        handler = StudentHandler()
        xml.sax.parse(file_path, handler)

        # очистка БД
        self.conn.execute("DELETE FROM students")

        for s in handler.students:
            self.add(s)
    def save_to_xml(self, file_path: str):
        doc = Document()
        root = doc.createElement("students")
        doc.appendChild(root)

        for s in self.get_all():
            student_el = doc.createElement("student")

            name_el = doc.createElement("full_name")
            name_el.appendChild(doc.createTextNode(s.full_name))

            group_el = doc.createElement("group")
            group_el.appendChild(doc.createTextNode(s.group))

            activities_el = doc.createElement("activities")
            activities_el.appendChild(
                doc.createTextNode(",".join(map(str, s.activities)))
            )

            student_el.appendChild(name_el)
            student_el.appendChild(group_el)
            student_el.appendChild(activities_el)

            root.appendChild(student_el)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(doc.toprettyxml(indent="  "))
    def _create_table(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            group_name TEXT,
            sem1 INTEGER,
            sem2 INTEGER,
            sem3 INTEGER,
            sem4 INTEGER,
            sem5 INTEGER,
            sem6 INTEGER,
            sem7 INTEGER,
            sem8 INTEGER,
            sem9 INTEGER,
            sem10 INTEGER
        )
        """)
        self.conn.commit()

  
    def _row_to_student(self, row) -> Student:
        return Student(
            id=row[0],
            full_name=row[1],
            group=row[2],
            activities=list(row[3:13])
        )

    
    def add(self, student: Student):
        if len(student.activities) != 10:
            raise ValueError(f"Ожидалось 10 значений, получено {len(student.activities)}")

        self.conn.execute("""
        INSERT INTO students (
            full_name, group_name,
            sem1, sem2, sem3, sem4, sem5,
            sem6, sem7, sem8, sem9, sem10
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student.full_name, student.group, *student.activities))

        self.conn.commit()

   
    def get_all(self) -> List[Student]:
        cursor = self.conn.execute("SELECT * FROM students")
        return [self._row_to_student(row) for row in cursor.fetchall()]

    
    def _filter(self, name=None, group=None, min_val=None, max_val=None):
        result = self.get_all()

        if name:
            result = [
                s for s in result
                if s.full_name.lower().startswith(name.strip().lower())
            ]

        if group:
            result = [
                s for s in result
                if str(s.group).strip() == group.strip()
            ]

        if min_val is not None or max_val is not None:
            result = [
                s for s in result
                if any(
                    (min_val is None or x >= min_val) and
                    (max_val is None or x <= max_val)
                    for x in s.activities
                )
            ]

        return result

    def search(self, name=None, group=None, min_val=None, max_val=None):
        return self._filter(name, group, min_val, max_val)

   
    def delete(self, name=None, group=None, min_val=None, max_val=None) -> int:
        to_delete = self._filter(name, group, min_val, max_val)

        for s in to_delete:
            self.conn.execute(
                "DELETE FROM students WHERE id=?",
                (s.id,)
            )

        self.conn.commit()
        return len(to_delete)