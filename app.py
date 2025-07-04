
import pickle
from collections import UserDict
from datetime import datetime, timedelta

# ----------- Класи поля -----------

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

# ----------- Клас Record -----------

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone_to_remove = self.find_phone(phone_number)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)
        else:
            raise ValueError(f"Phone {phone_number} not found.")

    def edit_phone(self, old_phone, new_phone):       
        new_phone_obj = Phone(new_phone)
        self.remove_phone(old_phone)
        self.phones.append(new_phone_obj)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None
        
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(phone.value for phone in self.phones)
        birthday = f", birthday: {self.birthday}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{birthday}"

# ----------- Клас AddressBook -----------

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)

                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)

                delta = (bday_this_year - today).days
                if 0 <= delta <= 7:
                    greeting_day = bday_this_year
                    if greeting_day.weekday() >= 5:
                        greeting_day += timedelta(days=7 - greeting_day.weekday())
                    upcoming.append({"name": record.name.value, "birthday": greeting_day.strftime("%d.%m.%Y")})
        return upcoming
    
    def __str__(self):
        result = ""
        for record in self.data.values():
            result += str(record) + "\n"
        return result.strip()

# ----------- Збереження/Завантаження -----------

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# ----------- Декоратор обробки помилок -----------

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Error: Contact not found."
        except ValueError as e:
            return f"Value Error: {e}"
        except IndexError:
            return "Enter all required arguments."
    return inner

# ----------- Функції-хендлери -----------

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return f"Contact '{name}' not found."
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return f"Contact '{name}' not found."
    return '; '.join(p.value for p in record.phones)

def show_all(book: AddressBook):
    return str(book) if book.data else "No contacts saved."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if not record:
        return f"Contact '{name}' not found."
    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return f"No birthday found for contact '{name}'."
    return record.birthday.value

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    return '\n'.join([f"{entry['name']} - {entry['birthday']}" for entry in upcoming])

# ----------- Парсер команд -----------

def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    return parts[0].lower(), parts[1:]

# ----------- Help -----------

def show_help():
    return (
        "Available commands:\n"
        "  hello                         - Greet the bot\n"
        "  add <name> <phone>            - Add a new contact or phone\n"
        "  change <name> <old> <new>     - Change a phone number\n"
        "  phone <name>                  - Show phone numbers\n"
        "  all                           - Show all contacts\n"
        "  add-birthday <name> <DD.MM.YYYY> - Add birthday\n"
        "  show-birthday <name>          - Show birthday\n"
        "  birthdays                     - Show upcoming birthdays\n"
        "  help                          - Show this help\n"
        "  close / exit                  - Exit bot"
    )

# ----------- Основна функція -----------

def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        elif command == "help":
            print(show_help())
        else:
            print("Invalid command. Type 'help' to see available commands.")

# ----------- Запуск -----------

if __name__ == "__main__":
    main()

