import secrets
import string

def random_string():
    res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(5))  
    return res

async def generate_code():
    return f"{random_string()}-{random_string()}-{random_string()}-{random_string()}"

