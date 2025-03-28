import sys
import sqlite3
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QDialog


# Класс главного окна
class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        # Создаем таблицу в БД при первом запуске
        self.create_table()
        self.load_data()
        # 1
        # Привязываем кнопки
        self.btnAdd.clicked.connect(self.open_add_form)
        self.btnEdit.clicked.connect(self.open_edit_form)

    def create_table(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coffee (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sort_name TEXT NOT NULL,
                degree TEXT NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                size INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def load_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM coffee")

        # Очистка таблицы
        self.tableWidget.setRowCount(0)

        # Заполнение таблицы
        for row_num, row_data in enumerate(cursor.fetchall()):
            self.tableWidget.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.tableWidget.setItem(row_num, col_num, QTableWidgetItem(str(data)))

        conn.close()

    def open_add_form(self):
        self.add_form = CoffeeForm()
        self.add_form.exec()
        self.load_data()  # Обновляем таблицу после закрытия формы

    def open_edit_form(self):
        selected = self.tableWidget.currentRow()
        if selected >= 0:
            try:
                # Безопасное получение ID
                coffee_id = int(self.tableWidget.item(selected, 0).text())
                self.edit_form = CoffeeForm(coffee_id)
                self.edit_form.exec()
                self.load_data()
            except Exception as e:
                print(f"Ошибка при открытии формы редактирования: {e}")


# Класс формы добавления/редактирования
class CoffeeForm(QDialog):
    def __init__(self, coffee_id=None):
        super().__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)

        # Заполняем комбобоксы
        self.roastInput.addItems(['Светлая', 'Средняя', 'Тёмная'])
        self.typeInput.addItems(['Молотый', 'В зернах'])

        # Если редактирование
        self.coffee_id = coffee_id
        if coffee_id:
            self.load_coffee_data()

        self.saveButton.clicked.connect(self.save_data)

    def load_coffee_data(self):
        try:
            conn = sqlite3.connect('coffee.sqlite')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM coffee WHERE id=?", (self.coffee_id,))
            data = cursor.fetchone()
            conn.close()

            if not data:
                raise ValueError(f"Запись с ID {self.coffee_id} не найдена")

            self.nameInput.setText(data[1])
            self.roastInput.setCurrentText(data[2])
            self.typeInput.setCurrentText(data[3])
            self.flavorInput.setText(data[4])
            self.priceInput.setValue(data[5])
            self.volumeInput.setValue(data[6])

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")
            self.close()

    def save_data(self):
        conn = sqlite3.connect('coffee.sqlite')
        cursor = conn.cursor()

        data = (
            self.nameInput.text(),
            self.roastInput.currentText(),
            self.typeInput.currentText(),
            self.flavorInput.text(),
            self.priceInput.value(),
            self.volumeInput.value()
        )

        if self.coffee_id:
            cursor.execute('''
                UPDATE coffee SET 
                    sort_name=?, degree=?, type=?, description=?, price=?, size=?
                WHERE id=?
            ''', data + (self.coffee_id,))
        else:
            cursor.execute('''
                INSERT INTO coffee 
                    (sort_name, degree, type, description, price, size)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', data)

        conn.commit()
        conn.close()
        self.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())