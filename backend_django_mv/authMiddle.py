from rest_framework import permissions
import jwt
import os
from users.models import User
class JWTAuthentication(permissions.BasePermission):

    def has_permission(self, request, view):
        SECRET_KEY = os.environ.get('SECRET_KEY')
        token = request.headers.get('Authorization')
        if not token:
            return False  # No token provided
        try:
            token = token.split(" ")[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            request.user = User.objects.get(id=payload['user_id'])  #Assign the User object to request.user for further use
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
        except User.DoesNotExist:
            return False
        except KeyError:
            return False
        except Exception as e:
            print("Error during JWT verification:", e)
            return False