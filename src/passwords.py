import base64
import hashlib
import hmac
import secrets

ITERATIONS = 600000


def hash_password(password):
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return '$'.join(('pbkdf2_sha256', str(ITERATIONS), base64.b64encode(salt).decode('ascii'), base64.b64encode(derived).decode('ascii')))


def verify_password(password, encoded):
    if not isinstance(password, str):
        return False
    valid = False
    salt, expected = bytes(16), bytes(32)
    try:
        algorithm, iterations, salt_text, hash_text = encoded.split('$')
        parsed_salt = base64.b64decode(salt_text, validate=True)
        parsed_hash = base64.b64decode(hash_text, validate=True)
        if algorithm == 'pbkdf2_sha256' and iterations == str(ITERATIONS) and len(parsed_salt) == 16 and len(parsed_hash) == 32:
            salt, expected, valid = parsed_salt, parsed_hash, True
    except (ValueError, TypeError, AttributeError):
        pass
    # Mesmo custo para hash ausente/malformado, sem derivar iterações do input.
    actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return hmac.compare_digest(actual, expected) and valid
