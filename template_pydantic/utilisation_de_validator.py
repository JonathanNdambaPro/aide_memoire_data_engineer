from typing import List
from pydantic import BaseModel, ValidationError, validator


class UserModel(BaseModel):
    """Exemple de base"""
    name: str
    username: str
    password1: str
    password2: str

    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('must contain a space')
        return v.title()

    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ValueError('passwords do not match')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'must be alphanumeric'
        return v

#------------------------------------------------------------------------
from pydantic import BaseModel, validator


def normalize(name: str) -> str:
    return ' '.join((word.capitalize()) for word in name.split(' '))


class Producer(BaseModel):
    """Manire plus consise si repetition de validator"""
    name: str

    # validators
    _normalize_name = validator('name', allow_reuse=True)(normalize)


class Consumer(BaseModel):
    """Manire plus consise si repetition de validator"""
    name: str

    # validators
    _normalize_name = validator('name', allow_reuse=True)(normalize)



#------------------------------------------------------------------------


class DemoModel(BaseModel):
    """utilisation de each item"""
    square_numbers: List[int] = []
    cube_numbers: List[int] = []

    # '*' is the same as 'cube_numbers', 'square_numbers' here:
    @validator('*', pre=True)
    def split_str(cls, v):
        if isinstance(v, str):
            return v.split('|')
        return v

    @validator('cube_numbers', 'square_numbers')
    def check_sum(cls, v):
        if sum(v) > 42:
            raise ValueError('sum of numbers greater than 42')
        return v

    @validator('square_numbers', each_item=True) #'each_item=True' permet de verifier la condition pour chaque item d'une collection
    def check_squares(cls, v):
        assert v ** 0.5 % 1 == 0, f'{v} is not a square number'
        return v

    @validator('cube_numbers', each_item=True)
    def check_cubes(cls, v):
        # 64 ** (1 / 3) == 3.9999999999999996 (!)
        # this is not a good way of checking cubes
        assert v ** (1 / 3) % 1 == 0, f'{v} is not a cubed number'
        return v

if __name__ == "__main__":
    user = UserModel(
    name='samuel colvin',
    username='scolvin',
    password1='zxcvbn',
    password2='zxcvbn',
    )
    print(user)
    try:
        UserModel(
            name='samuel',
            username='scolvin',
            password1='zxcvbn',
            password2='zxcvbn2',
        )
    except ValidationError as e:
        print(e)
        """
        2 validation errors for UserModel
        name
        must contain a space (type=value_error)
        password2
        passwords do not match (type=value_error)
        """
#------------------------------------------------------------------------
    jane_doe = Producer(name='JaNe DOE')
    john_doe = Consumer(name='joHN dOe')
    assert jane_doe.name == 'Jane Doe'
    assert john_doe.name == 'John Doe'

#------------------------------------------------------------------------
    print(DemoModel(square_numbers=[1, 4, 9]))
    #> square_numbers=[1, 4, 9] cube_numbers=[]
    print(DemoModel(square_numbers='1|4|16'))
    #> square_numbers=[1, 4, 16] cube_numbers=[]
    print(DemoModel(square_numbers=[16], cube_numbers=[8, 27]))
    #> square_numbers=[16] cube_numbers=[8, 27]
    try:
        DemoModel(square_numbers=[1, 4, 2])
    except ValidationError as e:
        print(e)
        """
        1 validation error for DemoModel
        square_numbers -> 2
        2 is not a square number (type=assertion_error)
        """

    try:
        DemoModel(cube_numbers=[27, 27])
    except ValidationError as e:
        print(e)