from flask import session
from shopping_mall.db_model import User

def current_user():
    """현재 로그인한 사용자 객체를 반환"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
