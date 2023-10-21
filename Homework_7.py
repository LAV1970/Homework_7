from collections import UserDict
import re
from datetime import datetime
import json


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    def __init__(self, value=None):
        super().__init__(value)


class Phone(Field):
    def __init__(self, value=None):
        if not Phone.is_valid_phone(value):
            raise ValueError("Invalid phone number format")
        super().__init__(value)

    @staticmethod
    def is_valid_phone(phone):
        # Обновленное регулярное выражение для номера телефона (ровно 10 цифр)
        pattern = r"^\+?\d{10}$|^\d{10}$"
        return bool(re.match(pattern, phone))


class BirthdayField(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", new_value):
            raise ValueError("Birthday must be in the format YYYY-MM-DD")
        self._value = new_value


class Record:
    def __init__(self, name, phone, email, birthday=None):
        self.name = Name(name)
        self.phone = Phone(phone)
        self.email = Field(email)
        self.birthday = BirthdayField(birthday)

    def days_to_birthday(self):
        if self.birthday.value is None:
            return None

        try:
            birthdate = datetime.strptime(self.birthday.value, "%Y-%m-%d")
        except ValueError:
            return None

        current_date = datetime.now()
        next_birthday = datetime(current_date.year, birthdate.month, birthdate.day)

        if current_date > next_birthday:
            next_birthday = next_birthday.replace(year=current_date.year + 1)

        days_until_birthday = (next_birthday - current_date).days
        return days_until_birthday


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        if name in self.data:
            return self.data[name]
        else:
            return None

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        else:
            return False

    def save_to_file(self, filename):
        data = {
            "records": [
                {
                    "name": record.name.value,
                    "phone": record.phone.value,
                    "email": record.email.value,
                    "birthday": record.birthday.value,
                }
                for record in self.data.values()
            ]
        }

        with open(filename, "w") as file:
            json.dump(data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)

            for record_data in data.get("records", []):
                name = record_data.get("name")
                phone = record_data.get("phone")
                email = record_data.get("email")
                birthday = record_data.get("birthday")

                record = Record(name, phone, email, birthday)
                self.add_record(record)
        except (FileNotFoundError, json.JSONDecodeError):
            # Обробка винятків, якщо файл відсутній або містить некоректні дані
            pass

    def search(self, query):
        results = []
        query = query.lower()
        for record in self.data.values():
            if (
                query in record.name.value.lower()
                or query in record.phone.value
                or query in record.email.value.lower()
            ):
                results.append(record)
        return results


if __name__ == "__main__":
    # Створюємо об'єкт адресної книги
    address_book = AddressBook()

    while True:
        print("Меню:")
        print("1. Додати запис")
        print("2. Зберегти в файл")
        print("3. Завантажити з файлу")
        print("4. Пошук")
        print("5. Вихід")

        choice = input("Виберіть опцію: ")

        if choice == "1":
            name = input("Ім'я: ")
            phone = input("Телефон: ")
            email = input("Email: ")
            birthday = input("Дата