####################################################
#                SIGNATURE VERIFICATION            #
####################################################

from jwt.algorithms import RSAAlgorithm
from dotenv import load_dotenv
import requests
import json
import jwt
import os

# Load environment variables
load_dotenv()
userpoolid = os.getenv('USERPOOL_ID')
region = os.getenv('REGION')

# Construct JWKS URL
jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}/.well-known/jwks.json"
expected_issuer = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}"

# Fetch JWKS
response = requests.get(jwks_url)
if response.status_code == 200:
  
    jwt_token = "eyJraWQiOiJTbXNyRVFUcHhkQW9aS0V4YzZsdHFIVkRPOGJNckxBXC9YSHBuUmhcL1NHM1E9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI0NWJkMTBjMi03YjNiLTQ2M2EtYjE1Zi04NDhlZTQ2ZTJmOTgiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV84ZHY1TnUzZEQiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiIyNjZzYmRsOW5jN284M251Y2xzYXBlOWhmaiIsIm9yaWdpbl9qdGkiOiI2MDQwMDliZi01YWVlLTQ2M2MtOGFiYy01YzdmYWYxNDA5NjYiLCJldmVudF9pZCI6Ijk4NDg4ZmFkLTYzYWEtNGYzZi04ZjJmLTFjZjM5YzY4YTNjYiIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoic2lnbmluZy1jaGF0YWRleFwvcmVhZCIsImF1dGhfdGltZSI6MTcwNzMwMzEzNiwiZXhwIjoxNzA3MzA2NzM2LCJpYXQiOjE3MDczMDMxMzYsImp0aSI6IjBlZjRhYzZmLWRmNWMtNDIxNy04Zjc3LTNiMmZjZDczYzRkMCIsInVzZXJuYW1lIjoicm9zaGFuLnBvdWRlbCJ9.FvaDYFhJ719dfVt0MCMPxZVRJn5esYlEcuF9V2W9zkjLWEqx7Sz4Rw8DeDZYtYdN_gHu_abbmjvtmHIZrujJL-0MZKJ3o53lYDYl0FWArHDl-MWhLUwvchbTyHxQkPhCJRlj2g_xc6ntezAgyMWOE0mrZz2loMgQDBxyLCJyKLz5EnTxh3bqpy_rwrJCmnxX_AuvCn1gErr9pdXdJP9pY_s1wUAsjfIc51ttJs6JsAf6iqCD91x0TRl0nhnRPxnWCaz6OpHUxWRhRg759JJzhgJ0bKkLuUHapdxmFLn-I83QvX6LOGQ1Q6eiogihpNFpdmoYpJGzqWzo_2vmLWaZzw"
    unverified_token_header = jwt.get_unverified_header(jwt_token)
    
    # finds the Match with 'key_id' obtain from access_token with jwks_uri['keys']
    jwk = next((key for key in response.json()['keys'] if key['kid'] == unverified_token_header['kid']), None)
    if jwk:
        public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))
        # from cryptography.hazmat.primitives import serialization
        # # print(public_key)
        # pem = public_key.public_bytes(
        #   encoding=serialization.Encoding.PEM,
        #   format=serialization.PublicFormat.SubjectPublicKeyInfo
        # )
        # print(pem.decode('utf-8'))
        try:
            decoded_token = jwt.decode(
              jwt_token,
              public_key,
              algorithms=[jwk['alg']],
              issuer=expected_issuer,
            )
            print("Signature Verified!")
        except jwt.ExpiredSignatureError:
            print("JWT Token has expired.")
        except jwt.exceptions.InvalidSignatureError:
            print("Invalid signature.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("Public key not found for the specified key Id")
else:
    print("Failed to fetch Token:", response.status_code)