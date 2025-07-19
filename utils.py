from pydantic import BaseModel, model_validator


class Phone(BaseModel):
    number: str

    @model_validator(mode='after')
    def set_phone_number(self):
        try:
            nm_dig = int(self.number[2:])
        except ValueError:
            raise ValueError("Номер телефона должен состоять из чисел, а не из букв!\n\n")
        if not (len(self.number[2:]) == 10 and isinstance(nm_dig, int)):
            raise ValueError("Номер телефона должен содержать 10 чисел после '+7'\n\n")
        if (self.number[0] == '7') or (self.number[1] == '7'):
            self.number = f"+7({self.number[2:5]}){self.number[5:8]}-{self.number[8:10]}-{self.number[10:12]}"
        return self


# try:
#     phone = Phone(number='+79204403999').model_dump()
#     print(phone)
# except ValueError as e:
#     print(f'Ошибка {e}')