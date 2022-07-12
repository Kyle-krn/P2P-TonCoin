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



def trim_float(digit: float):
    digit_split = str(digit).split(".")
    if len(digit_split[1]) > 2:
        digit_split[1] = digit_split[1][:len(digit_split[1]) - (len(digit_split[1]) - 2)]

    if digit_split[1] == "0":
        return int(digit_split[0])
    return float(".".join(digit_split))