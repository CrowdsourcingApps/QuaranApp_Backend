import uuid


def check_if_valid_uuid(string: str):
    try:
        uuid.UUID(string, version=4)
        return True
    except ValueError:
        return False
