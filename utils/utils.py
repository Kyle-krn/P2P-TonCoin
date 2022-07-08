import secrets
import string


def str_bool(str_bool: str):
    if str_bool == 'True':
        return True
    if str_bool == 'False':
        return False
    if str_bool == 'None':
        return None
    
def random_string():
    res = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(5))  
    return res

async def generate_code():
    return f"{random_string()}-{random_string()}-{random_string()}-{random_string()}"

