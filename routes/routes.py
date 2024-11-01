from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from typing import List, Optional
from models import Employee, User, Token
from utils import create_access_token, verify_password, get_password_hash, decode_access_token
from beanie import PydanticObjectId

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_user(username: str) -> Optional[User]:
    return await User.find_one({"username": username})

async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user or not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=dict)
async def register(user: User):
    existing_user = await get_user(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, password=hashed_password)
    await new_user.insert()
    
    return {"msg": "User registered successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    expires_at = datetime.now(timezone.utc) + access_token_expires
    new_token = Token(
        username=user.username,
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at
    )
    
    await new_token.insert()

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/employees/", response_model=List[Employee])
async def get_all_employees(current_user: User = Depends(get_current_user)):
    employees = await Employee.find_all().to_list()
    if not employees:
        raise HTTPException(status_code=404, detail="No employees found.")
    return employees

@router.get("/employees/{employee_id}", response_model=Employee)
async def get_employee_by_id(employee_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    employee = await Employee.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@router.get("/employees/filter/", response_model=List[Employee])
async def filter_employees(
    emp_salary: Optional[int] = Query(None, description="Filter by salary"),
    emp_position: Optional[str] = Query(None, description="Filter by position"),
    current_user: User = Depends(get_current_user) 
):
    query = {}   
    if emp_salary is not None:
        query["emp_salary"] = emp_salary
    
    if emp_position is not None:
        query["emp_position"] = {"$regex": emp_position, "$options": "i"}
    
    employees = await Employee.find(query).to_list()
    return employees

@router.post("/employees/", response_model=Employee)
async def create_employee(employee: Employee):
    await employee.insert()  
    return employee

@router.put("/employees/{employee_id}", response_model=Employee)
async def update_employee(employee_id: PydanticObjectId, updated_data: Employee, current_user: User = Depends(get_current_user)):
    employee = await Employee.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    updated_employee = employee.model_copy(update=updated_data.model_dump())
    await updated_employee.save()
    return updated_employee

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: PydanticObjectId, current_user: User = Depends(get_current_user)):
    employee = await Employee.get(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    await employee.delete()
    return {"message":"Employee deleted successfully"}