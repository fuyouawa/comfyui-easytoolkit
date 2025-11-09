import base64

def b64decode(data: str, encoding: str = "utf-8") -> bytes:
    return base64.b64decode(data.encode(encoding))

def b64encode(data: bytes, encoding: str = "utf-8") -> str:
    return base64.b64encode(data).decode(encoding)