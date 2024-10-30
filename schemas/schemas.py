def individual_data(employee):
    return {
        "id": str(employee["_id"]),
        "Employee ID" : employee["emp_id"],
        "Employee Name" : employee["emp_name"],
        "Employee Salary" : employee["emp_salary"],
        "Employee Position": employee["emp_position"]
    }

def all_data(employees):
    return [individual_data(employee) for employee in employees]