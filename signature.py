####################################################
#                SIGNATURE VERIFICATION            #
####################################################

from jwt.algorithms import RSAAlgorithm
from dotenv import load_dotenv
import requests
import json
import jwt
import os

# Adjusted to take access_token directly
async def signature_verification(access_token):
  load_dotenv()
  userpoolid = os.getenv('USERPOOL_ID')
  region = os.getenv('REGION')

  # Construct JWKS URL
  jwks_url = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}/.well-known/jwks.json"
  expected_issuer = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}"

  # Fetch JWKS
  response = requests.get(jwks_url)
  if response.status_code == 200:
      unverified_token_header = jwt.get_unverified_header(access_token)
      
      # Finds the match with 'kid' from JWKS
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
                access_token,
                public_key,
                algorithms=[jwk['alg']],
                issuer=expected_issuer,
              )
              return {"message": "Signature Verified!"}
          except jwt.ExpiredSignatureError:
              return {"error": "JWT Token has expired."}
          except jwt.exceptions.InvalidSignatureError:
              return {"error": "Invalid signature."}
          except Exception as e:
              return {"error": f"An error occurred: {str(e)}"}
      else:
          return {"error": "Public key not found for the specified key Id"}
  else:
      return {"error": f"Failed to fetch JWKS: {response.status_code}"}