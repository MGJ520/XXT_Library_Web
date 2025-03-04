# 使用Flask的SECRET_KEY作为JWT签名密钥
from datetime import timedelta, datetime, timezone

import jwt

from config import WEB_EXPIRATION_DATE

JWT_SECRET_KEY = 'your_secret_key'

# 使用HS256算法
JWT_ALGORITHM = 'HS256'

# JWT过期时间
JWT_EXPIRATION_DELTA = timedelta(hours=WEB_EXPIRATION_DATE)


# 创建JWT
def create_jwt(user_name, user_email):
    """
    创建JWT令牌。
    :param user_name:
    :param user_email: 用户的电子邮件地址，作为用户标识。
    :return: JWT令牌。
    """
    payload = {
        'user_email': user_email,
        'user_name': user_name,
        'exp': datetime.now(timezone.utc) + JWT_EXPIRATION_DELTA  # 使用时区感知的UTC时间
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


# 验证JWT
def verify_jwt(token):
    """
    验证JWT令牌。
    :param token: JWT令牌。
    :return: 如果验证成功，返回用户电子邮件地址；否则返回None。
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload['user_email']
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        return None
    except jwt.InvalidTokenError:
        # 无效的令牌
        return None