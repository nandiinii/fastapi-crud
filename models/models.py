from pydantic import field_validator, Field
from beanie import Document
from typing import Optional

class NameValidator:
    @staticmethod
    def validate_name(name: str) -> str:
        if any(char.isdigit() for char in name):
            raise ValueError("Name should not contain numbers")
        return name

class Employee(Document):
    emp_name : str = Field(...,title="Employee Name",min_length=1, max_length=100)
    emp_id : int = Field(..., title="Employee ID", gt=0)
    emp_address : Optional[str] = Field(None, title="Employee Address")
    emp_salary : int = Field(..., title="Employee Salary", gt=0)
    emp_position : str = Field(...,title="Employee Position", min_length=1)

    # @field_validator("emp_salary")
    # def salary_must_be_positive(cls, v):
    #     if v <= 0:
    #         raise ValueError("Salary must be positive")
    #     return v
    
    @field_validator("emp_name")
    def validate_emp_name(cls, v):
        return NameValidator.validate_name(v)
    
    class Settings:
        collection = "employee_data"

class User(Document):
    username : str = Field(..., title="Username", min_length=3, max_length=50)
    password : str = Field(...,title="Hashed Password")

    class Settings:
        collection="user_data"

class Token(Document):
    access_token : str = Field(..., title="Access Token")
    token_type : str = Field(..., title="Token Type")

    class Settings:
        collection = "token_data"