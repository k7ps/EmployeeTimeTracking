import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="employee_time_tracking.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        # Таблица настроек рабочего времени
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_settings (
            id INTEGER PRIMARY KEY,
            start_time TEXT,
            end_time TEXT
        )''')

        self.cursor.execute("SELECT COUNT(*) FROM work_settings")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute("INSERT INTO work_settings (start_time, end_time) VALUES (?, ?)",
                               ("09:00", "18:00"))

        # Таблица сотрудников
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date TEXT NOT NULL
        )''')

        # Таблица учета рабочего времени
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS time_records (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            date TEXT,
            arrival_time TEXT,
            departure_time TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
        )''')

        self.conn.commit()

    def add_employee(self, name, position, hire_date):
        self.cursor.execute("INSERT INTO employees (name, position, hire_date) VALUES (?, ?, ?)",
                          (name, position, hire_date))
        self.conn.commit()
        return self.cursor.lastrowid

    def remove_employee(self, employee_id):
        self.cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
        self.conn.commit()

    def get_all_employees(self):
        self.cursor.execute("SELECT id, name, position, hire_date FROM employees ORDER BY name")
        return self.cursor.fetchall()

    def get_employee(self, employee_id):
        self.cursor.execute("SELECT id, name, position, hire_date FROM employees WHERE id = ?", (employee_id,))
        return self.cursor.fetchone()

    def add_time_record(self, employee_id, date, arrival_time, departure_time):
        self.cursor.execute(
            "SELECT id FROM time_records WHERE employee_id = ? AND date = ?",
            (employee_id, date)
        )
        record = self.cursor.fetchone()

        if record:
            self.cursor.execute(
                "UPDATE time_records SET arrival_time = ?, departure_time = ? WHERE id = ?",
                (arrival_time, departure_time, record[0])
            )
        else:
            self.cursor.execute(
                "INSERT INTO time_records (employee_id, date, arrival_time, departure_time) VALUES (?, ?, ?, ?)",
                (employee_id, date, arrival_time, departure_time)
            )

        self.conn.commit()

    def get_time_records(self, employee_id):
        self.cursor.execute(
            "SELECT date, arrival_time, departure_time FROM time_records WHERE employee_id = ? ORDER BY date DESC",
            (employee_id,)
        )
        return self.cursor.fetchall()

    def get_work_settings(self):
        self.cursor.execute("SELECT start_time, end_time FROM work_settings WHERE id = 1")
        return self.cursor.fetchone()

    def update_work_settings(self, start_time, end_time):
        self.cursor.execute("UPDATE work_settings SET start_time = ?, end_time = ? WHERE id = 1",
                          (start_time, end_time))
        self.conn.commit()

    def get_employee_stats(self, employee_id):
        work_settings = self.get_work_settings()
        work_start = datetime.strptime(work_settings[0], "%H:%M").time()
        work_end = datetime.strptime(work_settings[1], "%H:%M").time()

        self.cursor.execute(
            "SELECT date, arrival_time, departure_time FROM time_records WHERE employee_id = ?",
            (employee_id,)
        )
        records = self.cursor.fetchall()

        if not records:
            return {
                "avg_delay": "0:00",
                "avg_overtime": "0:00",
                "avg_workday": "0:00"
            }

        total_delay_minutes = 0
        total_overtime_minutes = 0
        total_workday_minutes = 0
        count = 0

        for record in records:
            if not record[1] or not record[2]:
                continue

            arrival = datetime.strptime(record[1], "%H:%M").time()
            departure = datetime.strptime(record[2], "%H:%M").time()

            if arrival > work_start:
                delay_minutes = (arrival.hour * 60 + arrival.minute) - (work_start.hour * 60 + work_start.minute)
                total_delay_minutes += delay_minutes

            if departure > work_end:
                overtime_minutes = (departure.hour * 60 + departure.minute) - (work_end.hour * 60 + work_end.minute)
                total_overtime_minutes += overtime_minutes

            workday_minutes = (departure.hour * 60 + departure.minute) - (arrival.hour * 60 + arrival.minute)
            total_workday_minutes += workday_minutes

            count += 1

        if count == 0:
            return {
                "avg_delay": "0:00",
                "avg_overtime": "0:00",
                "avg_workday": "0:00"
            }

        avg_delay = total_delay_minutes / count
        avg_overtime = total_overtime_minutes / count
        avg_workday = total_workday_minutes / count

        return {
            "avg_delay": f"{int(avg_delay // 60)}:{int(avg_delay % 60):02d}",
            "avg_overtime": f"{int(avg_overtime // 60)}:{int(avg_overtime % 60):02d}",
            "avg_workday": f"{int(avg_workday // 60)}:{int(avg_workday % 60):02d}"
        }

    def get_company_stats(self):
        all_employees = self.get_all_employees()

        if not all_employees:
            return {
                "avg_delay": "0:00",
                "avg_overtime": "0:00",
                "avg_workday": "0:00"
            }

        total_delay_hours = 0
        total_delay_minutes = 0
        total_overtime_hours = 0
        total_overtime_minutes = 0
        total_workday_hours = 0
        total_workday_minutes = 0

        for employee in all_employees:
            stats = self.get_employee_stats(employee[0])

            delay_parts = stats["avg_delay"].split(":")
            overtime_parts = stats["avg_overtime"].split(":")
            workday_parts = stats["avg_workday"].split(":")

            total_delay_hours += int(delay_parts[0])
            total_delay_minutes += int(delay_parts[1])
            total_overtime_hours += int(overtime_parts[0])
            total_overtime_minutes += int(overtime_parts[1])
            total_workday_hours += int(workday_parts[0])
            total_workday_minutes += int(workday_parts[1])

        total_delay = total_delay_hours * 60 + total_delay_minutes
        total_overtime = total_overtime_hours * 60 + total_overtime_minutes
        total_workday = total_workday_hours * 60 + total_workday_minutes

        count = len(all_employees)
        avg_delay = total_delay / count
        avg_overtime = total_overtime / count
        avg_workday = total_workday / count

        return {
            "avg_delay": f"{int(avg_delay // 60)}:{int(avg_delay % 60):02d}",
            "avg_overtime": f"{int(avg_overtime // 60)}:{int(avg_overtime % 60):02d}",
            "avg_workday": f"{int(avg_workday // 60)}:{int(avg_workday % 60):02d}"
        }

    def close(self):
        self.conn.close()
