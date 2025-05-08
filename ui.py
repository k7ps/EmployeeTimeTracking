from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QLabel, QPushButton, QLineEdit, QDateEdit, QTimeEdit,
                              QTableWidget, QTableWidgetItem, QComboBox, QFormLayout,
                              QGroupBox, QTabWidget, QMessageBox, QHeaderView)
from PySide6.QtCore import QDate, QTime
from datetime import datetime
from models import Employee, TimeRecord

class MainWindow(QMainWindow):
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.setWindowTitle("Система учёта рабочего времени")
        self.setMinimumSize(800, 600)

        self.init_ui()
        self.refresh_employees_list()
        self.refresh_statistics()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Верхняя часть с настройками рабочего времени
        settings_group = QGroupBox("Настройки рабочего дня")
        settings_layout = QHBoxLayout(settings_group)

        # Получаем текущие настройки рабочего времени
        work_settings = self.database.get_work_settings()
        start_time = QTime.fromString(work_settings[0], "HH:mm")
        end_time = QTime.fromString(work_settings[1], "HH:mm")

        settings_layout.addWidget(QLabel("Начало рабочего дня:"))
        self.work_start_time = QTimeEdit(start_time)
        settings_layout.addWidget(self.work_start_time)

        settings_layout.addWidget(QLabel("Окончание рабочего дня:"))
        self.work_end_time = QTimeEdit(end_time)
        settings_layout.addWidget(self.work_end_time)

        save_settings_btn = QPushButton("Сохранить настройки")
        save_settings_btn.clicked.connect(self.save_work_settings)
        settings_layout.addWidget(save_settings_btn)

        main_layout.addWidget(settings_group)

        # Табы для разных функций
        tabs = QTabWidget()
        main_layout.addWidget(tabs)

        # Таб сотрудников
        employee_tab = QWidget()
        employee_layout = QHBoxLayout(employee_tab)

        # Левая часть - список сотрудников
        employee_list_group = QGroupBox("Список сотрудников")
        employee_list_layout = QVBoxLayout(employee_list_group)

        self.employee_table = QTableWidget(0, 4)
        self.employee_table.setHorizontalHeaderLabels(["ID", "ФИО", "Должность", "Дата найма"])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.employee_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.employee_table.selectionModel().selectionChanged.connect(self.on_employee_selected)
        self.employee_table.setColumnHidden(0, True)

        employee_list_layout.addWidget(self.employee_table)
        employee_layout.addWidget(employee_list_group)

        # Правая часть - добавление/удаление сотрудников
        employee_control_group = QGroupBox("Управление сотрудниками")
        employee_control_layout = QVBoxLayout(employee_control_group)

        # Форма добавления сотрудника
        add_form = QFormLayout()
        self.employee_name = QLineEdit()
        self.employee_position = QLineEdit()
        self.employee_hire_date = QDateEdit(QDate.currentDate())
        self.employee_hire_date.setDisplayFormat("dd.MM.yyyy")

        add_form.addRow("ФИО:", self.employee_name)
        add_form.addRow("Должность:", self.employee_position)
        add_form.addRow("Дата найма:", self.employee_hire_date)

        add_employee_btn = QPushButton("Добавить сотрудника")
        add_employee_btn.clicked.connect(self.add_employee)

        remove_employee_btn = QPushButton("Удалить сотрудника")
        remove_employee_btn.clicked.connect(self.remove_employee)

        employee_control_layout.addLayout(add_form)
        employee_control_layout.addWidget(add_employee_btn)
        employee_control_layout.addWidget(remove_employee_btn)

        employee_layout.addWidget(employee_control_group)

        # Таб учета времени
        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)

        # Выбор сотрудника
        employee_select_layout = QHBoxLayout()
        employee_select_layout.addWidget(QLabel("Выберите сотрудника:"))
        self.employee_combo = QComboBox()
        self.employee_combo.currentIndexChanged.connect(self.on_employee_combo_changed)
        employee_select_layout.addWidget(self.employee_combo)
        time_layout.addLayout(employee_select_layout)

        # Запись времени прихода и ухода
        time_record_group = QGroupBox("Запись времени")
        time_record_layout = QFormLayout(time_record_group)

        self.record_date = QDateEdit(QDate.currentDate())
        self.record_date.setDisplayFormat("dd.MM.yyyy")
        self.arrival_time = QTimeEdit(QTime(9, 0))
        self.departure_time = QTimeEdit(QTime(18, 0))

        time_record_layout.addRow("Дата:", self.record_date)
        time_record_layout.addRow("Время прихода:", self.arrival_time)
        time_record_layout.addRow("Время ухода:", self.departure_time)

        save_time_btn = QPushButton("Сохранить запись")
        save_time_btn.clicked.connect(self.save_time_record)
        time_record_layout.addRow(save_time_btn)

        time_layout.addWidget(time_record_group)

        # Таблица истории
        time_history_group = QGroupBox("История посещений")
        time_history_layout = QVBoxLayout(time_history_group)

        self.time_history_table = QTableWidget(0, 3)
        self.time_history_table.setHorizontalHeaderLabels(["Дата", "Время прихода", "Время ухода"])
        self.time_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        time_history_layout.addWidget(self.time_history_table)
        time_layout.addWidget(time_history_group)

        # Таб статистики
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)

        # Статистика сотрудника
        employee_stats_group = QGroupBox("Статистика по сотруднику")
        employee_stats_layout = QFormLayout(employee_stats_group)

        employee_stats_select = QHBoxLayout()
        employee_stats_select.addWidget(QLabel("Выберите сотрудника:"))
        self.stats_employee_combo = QComboBox()
        self.stats_employee_combo.currentIndexChanged.connect(self.refresh_employee_stats)
        employee_stats_select.addWidget(self.stats_employee_combo)

        employee_stats_layout.addRow(employee_stats_select)

        self.employee_avg_delay = QLabel("0:00")
        self.employee_avg_overtime = QLabel("0:00")
        self.employee_avg_workday = QLabel("0:00")

        employee_stats_layout.addRow("Среднее опоздание:", self.employee_avg_delay)
        employee_stats_layout.addRow("Средняя переработка:", self.employee_avg_overtime)
        employee_stats_layout.addRow("Средняя длительность рабочего дня:", self.employee_avg_workday)

        stats_layout.addWidget(employee_stats_group)

        # Статистика компании
        company_stats_group = QGroupBox("Статистика по компании")
        company_stats_layout = QFormLayout(company_stats_group)

        self.company_avg_delay = QLabel("0:00")
        self.company_avg_overtime = QLabel("0:00")
        self.company_avg_workday = QLabel("0:00")

        company_stats_layout.addRow("Среднее опоздание:", self.company_avg_delay)
        company_stats_layout.addRow("Средняя переработка:", self.company_avg_overtime)
        company_stats_layout.addRow("Средняя длительность рабочего дня:", self.company_avg_workday)

        stats_layout.addWidget(company_stats_group)

        # Добавляем все табы
        tabs.addTab(employee_tab, "Сотрудники")
        tabs.addTab(time_tab, "Учет времени")
        tabs.addTab(stats_tab, "Статистика")

    def save_work_settings(self):
        start_time = self.work_start_time.time().toString("HH:mm")
        end_time = self.work_end_time.time().toString("HH:mm")

        self.database.update_work_settings(start_time, end_time)
        self.refresh_statistics()

    def add_employee(self):
        name = self.employee_name.text().strip()
        position = self.employee_position.text().strip()
        hire_date = self.employee_hire_date.date().toString("yyyy-MM-dd")

        if not name or not position:
            QMessageBox.warning(self, "Предупреждение", "Имя и должность не могут быть пустыми")
            return

        self.database.add_employee(name, position, hire_date)

        self.employee_name.clear()
        self.employee_position.clear()

        self.refresh_employees_list()

    def remove_employee(self):
        selected_items = self.employee_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Предупреждение", "Выберите сотрудника для удаления")
            return

        row = selected_items[0].row()
        employee_id = int(self.employee_table.item(row, 0).text())
        employee_name = self.employee_table.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить сотрудника {employee_name}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.database.remove_employee(employee_id)
            self.refresh_employees_list()

    def on_employee_selected(self):
        pass

    def save_time_record(self):
        if self.employee_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите сотрудника")
            return

        employee_id = self.employee_combo.currentData()
        date = self.record_date.date().toString("yyyy-MM-dd")
        arrival_time = self.arrival_time.time().toString("HH:mm")
        departure_time = self.departure_time.time().toString("HH:mm")

        self.database.add_time_record(employee_id, date, arrival_time, departure_time)
        self.refresh_time_history(employee_id)
        self.refresh_statistics()

    def refresh_time_history(self, employee_id):
        records = self.database.get_time_records(employee_id)

        self.time_history_table.setRowCount(len(records))

        for row, record in enumerate(records):
            time_record = TimeRecord.from_db_row(record)

            date_obj = datetime.strptime(time_record.date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")

            self.time_history_table.setItem(row, 0, QTableWidgetItem(formatted_date))
            self.time_history_table.setItem(row, 1, QTableWidgetItem(time_record.arrival_time))
            self.time_history_table.setItem(row, 2, QTableWidgetItem(time_record.departure_time))

    def refresh_employees_list(self):
        employees = self.database.get_all_employees()

        self.employee_table.setRowCount(len(employees))

        for row, emp_data in enumerate(employees):
            employee = Employee.from_db_row(emp_data)

            self.employee_table.setItem(row, 0, QTableWidgetItem(str(employee.id)))
            self.employee_table.setItem(row, 1, QTableWidgetItem(employee.name))
            self.employee_table.setItem(row, 2, QTableWidgetItem(employee.position))

            date_obj = datetime.strptime(employee.hire_date, "%Y-%m-%d")
            formatted_date = date_obj.strftime("%d.%m.%Y")

            self.employee_table.setItem(row, 3, QTableWidgetItem(formatted_date))

        self.employee_combo.clear()
        self.stats_employee_combo.clear()

        for emp_data in employees:
            employee = Employee.from_db_row(emp_data)
            self.employee_combo.addItem(employee.name, employee.id)
            self.stats_employee_combo.addItem(employee.name, employee.id)

        if self.employee_combo.count() > 0:
            employee_id = self.employee_combo.currentData()
            self.refresh_time_history(employee_id)

    def refresh_employee_stats(self):
        if self.stats_employee_combo.currentIndex() < 0:
            return

        employee_id = self.stats_employee_combo.currentData()
        stats = self.database.get_employee_stats(employee_id)

        self.employee_avg_delay.setText(stats["avg_delay"])
        self.employee_avg_overtime.setText(stats["avg_overtime"])
        self.employee_avg_workday.setText(stats["avg_workday"])

    def refresh_statistics(self):
        company_stats = self.database.get_company_stats()

        self.company_avg_delay.setText(company_stats["avg_delay"])
        self.company_avg_overtime.setText(company_stats["avg_overtime"])
        self.company_avg_workday.setText(company_stats["avg_workday"])

        self.refresh_employee_stats()

    def on_employee_combo_changed(self, index):
        if index >= 0:
            employee_id = self.employee_combo.currentData()
            self.refresh_time_history(employee_id)
