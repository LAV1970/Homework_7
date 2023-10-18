from datetime import datetime
import json
import re


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


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
        self.name = Field(name)
        self.phone = PhoneField(phone)
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


class AddressBook:
    def __init__(self):
        self.records = []

    def add_record(self, record):
        self.records.append(record)

    def save_to_file(self, filename):
        data = {
            "records": [
                {
                    "name": record.name.value,
                    "phone": record.phone.value,
                    "email": record.email.value,
                    "birthday": record.birthday.value,
                }
                for record in self.records
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
        for record in self.records:
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
            birthday = input("Дата народження (рік-місяць-день): ")

            # Створюємо запис і додаємо його до адресної книги
            record = Record(name, phone, email, birthday)
            address_book.add_record(record)

        elif choice == "2":
            filename = input("Введіть ім'я файлу для збереження: ")
            address_book.save_to_file(filename)
            print(f"Дані збережено у файлі {filename}")

        elif choice == "3":
            filename = input("Введіть ім'я файлу для завантаження: ")
            address_book.load_from_file(filename)
            print(f"Дані завантажено з файлу {filename}")

        elif choice == "4":
            query = input("Введіть запит для пошуку: ")
            results = address_book.search(query)

            if results:
                print("Результати пошуку:")
                for record in results:
                    print(
                        f"Ім'я: {record.name.value}, Телефон: {record.phone.value}, Email: {record.email.value}"
                    )
            else:
                print("Збігів не знайдено")

        elif choice == "5":
            break
