def operate_on_data(data: list[int], operation: str) -> int:
    if operation == "sum":
        return sum(data)
    elif operation == "average":
        return sum(data) / len(data)
    else:
        raise ValueError(f"Invalid operation: {operation}")
