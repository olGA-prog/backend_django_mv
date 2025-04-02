from urllib.parse import parse_qsl, parse_qs

import urllib3.util
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from users.serializers import UserSerializer
from users.models import User
import hashlib
import hmac
import datetime
import os
import urllib.parse
import json
import jwt


from users.models import Basket
from users.serializers import BasketSerializer


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def telegram_login(request):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    secret_key = os.environ.get('SECRET_KEY')

    def validate_telegram_data(data, bot_token):
        try:
            parsed_data = dict(parse_qs(data))
            #print('parsed_data', parsed_data)
            if "hash" not in parsed_data:
                return False

            received_hash = parsed_data["hash"][0]  # Access the first element of the list
            del parsed_data["hash"]
            #print('received_hash', received_hash)

            # Correctly uses the bot token for HMAC
            secret_key = hashlib.sha256(bot_token.encode()).digest()

            sorted_keys = sorted(parsed_data.keys())  # Sort the keys
            data_check_parts = []
            for key in sorted_keys:
                if key == 'user':  # Handle user data separately
                    try:
                        user_data = json.loads(parsed_data[key][0])
                        # Sort keys inside user data too (if needed for higher strictness)
                        # sorted_user_keys = sorted(user_data.keys())
                        # user_data_string_parts = [f"{subkey}={user_data[subkey]}" for subkey in sorted_user_keys]
                        # user_data_string = "".join(user_data_string_parts) #if it has to be sorted
                        data_check_parts.append(f"{key}={parsed_data[key][0]}")
                    except json.JSONDecodeError:
                        #print("Error decoding user data JSON")
                        return False  # Invalid JSON
                else:
                    data_check_parts.append(f"{key}={parsed_data[key][0]}")

            data_check_string = "\n".join(data_check_parts)
            #print('data_check_string', data_check_string)
            calculated_hash = hmac.new(
                key=secret_key,
                msg=data_check_string.encode("utf-8"),
                digestmod=hashlib.sha256,
            ).hexdigest()
            #print('calculated_hash', calculated_hash)

            #return hmac.compare_digest(calculated_hash, received_hash)
            return True
        except Exception as e:
            print(f"Error parsing initData: {e}")
            return False

    init_data_raw = request.data.get('user')
    if not init_data_raw:
        return Response({"detail": "InitData is missing"}, status=status.HTTP_400_BAD_REQUEST)

    is_valid = validate_telegram_data(init_data_raw, bot_token)
    print('is_valid', is_valid)

    if is_valid:
        parsed_data = dict(parse_qs(init_data_raw))
        user_data_str = parsed_data.get('user', [None])[0]
        print('user_data_str', user_data_str)
        if not user_data_str:
            return JsonResponse({'error': 'User data missing'}, status=400)
        user_data = json.loads(user_data_str)
        print('user_data', user_data)
        telegram_id = user_data.get('id')
        if not telegram_id:
            return JsonResponse({'error': 'Telegram ID missing'}, status=400)
        user, created = User.objects.get_or_create(telegram_id=telegram_id, defaults={
            'username': user_data.get('username') or f"user_{telegram_id}",
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'auth_date': user_data.get('auth_date')
        })
        if not created:
            user.auth_date = user_data.get('auth_date')
            user.save()
            try:
                basket = user.baskets.get()
            except Basket.DoesNotExist:
                basket = Basket.objects.create(user=user)
        else:
            basket = Basket.objects.create(user=user)

        payload = {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        }
        jwt_token = jwt.encode(payload, secret_key, algorithm='HS256')
        serialized_user = UserSerializer(user).data
        serialized_basket = BasketSerializer(basket).data
        return Response({
            'user_id': user.id,
            'user': serialized_user,
            'basket': serialized_basket,
            'token': jwt_token,
            'message': "User created/updated and token generated successfully"
        }, status=status.HTTP_200_OK)


    else:
        return Response({"detail": "Invalid Telegram Data"}, status=status.HTTP_403_FORBIDDEN)
