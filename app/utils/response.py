from fastapi import HTTPException

def success_response(message: str, data=None):
    return {
        "success": True,
        "message": message,
        "data": data or {}
    }

def error_message(status_code: int, message:str):
    raise HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "message": message,
            "data": {}
        }
    )