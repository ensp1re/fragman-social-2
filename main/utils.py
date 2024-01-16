import random
import uuid

def get_random_code():
    namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
    name = 'example_name'

    code = str(uuid.uuid5(namespace, name))[:8].replace("-", "").lower()
    return code


def get_random_id_message():
    num1 = random.randint(100000000, 9999999999)
    num2 = random.randint(1000000000, 999999999999999999)

    return f"{num1}-{num2}"