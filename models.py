from datetime import datetime

class Employee:
    def __init__(self, id=None, name="", position="", hire_date=""):
        self.id = id
        self.name = name
        self.position = position
        self.hire_date = hire_date

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return Employee(row[0], row[1], row[2], row[3])

class TimeRecord:
    def __init__(self, date="", arrival_time="", departure_time=""):
        self.date = date
        self.arrival_time = arrival_time
        self.departure_time = departure_time

    @staticmethod
    def from_db_row(row):
        if not row:
            return None
        return TimeRecord(row[0], row[1], row[2])
