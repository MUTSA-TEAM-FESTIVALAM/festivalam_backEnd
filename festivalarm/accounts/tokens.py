import jwt
import datetime
from my_secrets import JWT_ALGORITHM, JWT_SECRET_KEY


# --- JWT 토큰 발급 --- #
def generate_token(payload, type):
    if type == "access":
        # 2시간
        exp = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    elif type == "refresh":
        # 2주
        exp = datetime.datetime.utcnow() + datetime.timedelta(weeks=2)
    else:
        raise Exception("Invalid tokenType")
    
    payload['exp'] = exp        # 토큰 만료시각
    payload['iat'] = datetime.datetime.utcnow()     # 토큰 발행시각
    encoded = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    return encoded


# --- JWT 토큰 복호화 --- #
def decode_token(jwt_token):
    decoded = jwt.decode(jwt_token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)

    return decoded