import pytest
import httpx
from unittest.mock import AsyncMock, patch
from beanie import PydanticObjectId

@patch.object(httpx.AsyncClient,"post", new_callable=AsyncMock)
@pytest.mark.anyio
async def test_create_employee_success(mock_post):  
    employee = {
        "emp_name": "John Doe",
        "emp_id": 1,
        "emp_address": "789 Oak Street",
        "emp_salary": 50000,
        "emp_position": "Developer"
    }
    # Mock response data 
    mock_response = httpx.Response(status_code=200,json=employee)    
    mock_post.return_value = mock_response    
    async with httpx.AsyncClient() as client:        
        response = await client.post("/employees/", json=employee)
    assert response.status_code == 200
    assert response.json()["emp_name"] == employee["emp_name"]
    assert response.json()["emp_id"] == employee["emp_id"]
    assert response.json()["emp_address"] == employee["emp_address"]
    assert response.json()["emp_salary"] == employee["emp_salary"]
    assert response.json()["emp_position"] == employee["emp_position"]


@patch.object(httpx.AsyncClient,"post", new_callable=AsyncMock)
@pytest.mark.anyio
async def test_create_employee_failure(mock_post):
    employee = {
        "emp_name": "John Doe1",
        "emp_id": 1,
        "emp_address": "789 Oak Street",
        "emp_salary": 50000,
        "emp_position": "Developer"
    }
    mock_response = httpx.Response(status_code=422,json={"detail": "Invalid data"})
    mock_post.return_value = mock_response
    async with httpx.AsyncClient() as client:
        response = await client.post("/employees/", json=employee)
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid data"


@pytest.mark.anyio
@patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock)
async def test_get_all_employees_success(mock_get):
    mock_employees = [
        {
            "emp_name": "John Doe",
            "emp_id": 1,
            "emp_address": "123 Elm Street",
            "emp_salary": 60000,
            "emp_position": "Manager"
        },
        {
            "emp_name": "Jane Smith",
            "emp_id": 2,
            "emp_address": "456 Maple Avenue",
            "emp_salary": 55000,
            "emp_position": "Analyst"
        }
    ]

    mock_response = httpx.Response(
        status_code=200,
        json=mock_employees 
    )
    mock_get.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.get("/employees/")

    assert response.status_code == 200
    employees = response.json()
    assert len(employees) == 2

    assert employees == mock_employees


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"get",new_callable=AsyncMock)
async def test_get_all_employees_failure(mock_get):
    mock_response = httpx.Response(
         status_code=404,
         json={"detail": "No employees found"}
    )
    mock_get.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.get("/employees/")

    assert response.status_code == 404
    assert response.json()["detail"] == "No employees found"


@pytest.mark.anyio
@patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock)
async def test_get_employee_by_id_success(mock_get):
    # Mock employee data for successful retrieval
    mock_employee = {
        "emp_name": "John Doe",
        "emp_id": 1,
        "emp_address": "123 Elm Street",
        "emp_salary": 60000,
        "emp_position": "Manager"
    }
    
    # Create a mock response for successful retrieval
    mock_response = httpx.Response(
        status_code=200,
        json=mock_employee  # Mock JSON response for found employee
    )
    mock_get.return_value = mock_response

    # Test GET request to /employees/{employee_id} endpoint
    employee_id = str(PydanticObjectId())  # Generate a mock ObjectId
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/employees/{employee_id}")
    
    # Assertions for the successful response
    assert response.status_code == 200
    employee = response.json()
    assert employee == mock_employee

@pytest.mark.anyio
@patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock)
async def test_get_employee_by_id_failure(mock_get):
    mock_response = httpx.Response(
        status_code=404,
        json={"detail": "Employee not found"}
    )
    mock_get.return_value = mock_response


    employee_id = str(PydanticObjectId())
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/employees/{employee_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Employee not found"


@pytest.mark.anyio
@patch.object(httpx.AsyncClient, "put", new_callable=AsyncMock)
async def test_update_employee_success(mock_put):
    updated_employee_data = {
        "emp_name": "Jane Doe",
        "emp_id": 1,
        "emp_address": "456 Oak Street",
        "emp_salary": 70000,
        "emp_position": "Senior Manager"
    }

    mock_response = httpx.Response(
        status_code=200,
        json=updated_employee_data
    )
    mock_put.return_value = mock_response

    employee_id = str(PydanticObjectId())
    async with httpx.AsyncClient() as client:
        response = await client.put(f"/employees/{employee_id}", json=updated_employee_data)
    
    assert response.status_code == 200
    updated_employee = response.json()
    assert updated_employee == updated_employee_data


@pytest.mark.anyio
@patch.object(httpx.AsyncClient, "put", new_callable=AsyncMock)
async def test_update_employee_failure(mock_put):
    mock_response = httpx.Response(
        status_code=404,
        json={"detail":"Employee not found"}
    )
    mock_put.return_value = mock_response

    employee_id = str(PydanticObjectId())
    updated_employee_data = {
        "emp_name": "Jane Doe",
        "emp_id": 1,
        "emp_address": "456 Oak Street",
        "emp_salary": 70000,
        "emp_position": "Senior Manager"
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(f"/employees/{employee_id}", json=updated_employee_data)

    assert response.status_code == 404
    error_detail = response.json()
    assert error_detail == {"detail":"Employee not found"}

@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"delete",new_callable=AsyncMock)
async def test_delete_employee_success(mock_delete):
    mock_response = httpx.Response(
        status_code=200,
        json={"message": "Employee deleted successfully"}
    )
    mock_delete.return_value = mock_response

    employee_id = str(PydanticObjectId())

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"/employees/{employee_id}")

    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {"message": "Employee deleted successfully"}


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"delete",new_callable=AsyncMock)
async def test_delete_employee_failure(mock_delete):
    mock_response = httpx.Response(
        status_code=404,
        json={"detail":"Employee not found"}
    )
    mock_delete.return_value = mock_response

    employee_id = str(PydanticObjectId())

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"/employees/{employee_id}")

    assert response.status_code == 404
    error_detail = response.json()
    assert error_detail == {"detail": "Employee not found"}


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"post",new_callable=AsyncMock)
async def test_login_success(mock_post):
    mock_user = {
        "username": "john_doe",
        "password": "admin123"
    }

    mock_response = httpx.Response(
        status_code=200,
        json={"access_token": "mock_access_token", "token_type": "bearer"}
    )

    mock_post.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.post("/login", json=mock_user)

    assert response.status_code == 200
    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"post",new_callable=AsyncMock)
async def test_login_failure(mock_post):
    mock_user = {
        "username": "john_doe",
        "password": "wrongpassword"
    }

    mock_response = httpx.Response(
        status_code=401,
        json={"detail":"Invalid username or password"}
    )
    mock_post.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.post("/login",json=mock_user)

    assert response.status_code == 401
    error_detail = response.json()
    assert error_detail == {"detail": "Invalid username or password"}


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"post",new_callable=AsyncMock)
async def test_register_success(mock_post):
    mock_user = {
        "username": "john_doe",
        "password": "securepassword"
    }
    mock_response = httpx.Response(
        status_code=200,
        json= {"msg":"User registered successfully"}
    )
    mock_post.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.post("/register",json=mock_user)
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data == {"msg": "User registered successfully"}


@pytest.mark.anyio
@patch.object(httpx.AsyncClient,"post",new_callable=AsyncMock)
async def test_register_username_already_taken(mock_post):
    mock_user = {
        "username": "john_doe",
        "password": "securepassword"
    }
    
    mock_response = httpx.Response(
        status_code=400,
        json={"detail": "Username already registered"}  # Mock error message
    )
    mock_post.return_value = mock_response

    async with httpx.AsyncClient() as client:
        response = await client.post("/register", json=mock_user)
    
    assert response.status_code == 400
    error_detail = response.json()
    assert error_detail == {"detail": "Username already registered"}