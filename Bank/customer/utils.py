import bcrypt
import jwt
from datetime import datetime, timedelta
from .models import Token

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_jwt_tokens(customer_id):
    access_token_expiration = datetime.utcnow() + timedelta(minutes=15)
    refresh_token_expiration = datetime.utcnow() + timedelta(days=7)
    access_token_payload = {
        'customer_id': customer_id,
        'exp': access_token_expiration,
    }
    refresh_token_payload = {
        'customer_id': customer_id,
        'exp': refresh_token_expiration,
    }
    access_token = jwt.encode(access_token_payload, key='secret',algorithm="HS256")
    refresh_token = jwt.encode(refresh_token_payload, key='secret',algorithm="HS256")

    return {'access_token' : access_token, 'refresh_token' : refresh_token}

def refresh_jwt_token(refresh_token):
    refresh_token_payload = jwt.decode(refresh_token, 'secret', algorithms=['RS256'])
    customer_id = refresh_token_payload.get('customer_id')
    current_time = datetime.utcnow()
    refresh_token_exp = refresh_token_payload.get('exp')
    if refresh_token_exp and refresh_token_exp < current_time:
        raise jwt.ExpiredSignatureError('Refresh token has expired')

    access_token_expiration = current_time + timedelta(minutes=15)
    refresh_token_expiration = current_time + timedelta(days=7)
    access_token_payload = {
        'customer_id': customer_id,
        'exp': access_token_expiration,
    }
    refresh_token_payload = {
        'customer_id': customer_id,
        'exp': refresh_token_expiration,
    }
    access_token = jwt.encode(access_token_payload, 'secret', algorithm='RS256')
    refresh_token = jwt.encode(refresh_token_payload, 'secret', algorithm='RS256')
    return {'customer_id': customer_id,'access_token': access_token, 'refresh_token': refresh_token}

def verify_jwt_token(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        access_token = request.META['HTTP_AUTHORIZATION']
        payload = jwt.decode(access_token, 'secret', algorithm='RS256')
        token = Token.objects.get(customer_id=payload["customer_id"])
        if access_token == token.access_token:
            return {"status":True, "customer_id": payload["customer_id"]}
        else:
            return {"status":False}