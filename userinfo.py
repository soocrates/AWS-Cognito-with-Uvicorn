####################################################
#                Retrive USER-INFORMATION          #
####################################################

from dotenv import load_dotenv
import requests
import os

# The URL to retrieve user information
def retrive_user_information(access_token):
  load_dotenv()
  domain= os.getenv('HOSTED_UI_COGNITO_DOMAIN')
  region= os.getenv('REGION')
  url = f"https://{domain}.auth.{region}.amazoncognito.com/oauth2/userInfo"
  # Headers for the request
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Content-Type": "application/x-amz-json-1.1",
      "User-Agent": "ChatAdex/1.0",
      "Accept": "*/*",
      "Host": f"{domain}.auth.{region}.amazoncognito.com",
      "Accept-Encoding": "gzip, deflate, br",
      "Connection": "keep-alive"
  }
  # signing-chatadex/read.

  # Send the GET request
  response = requests.get(url, headers=headers)

  # Check if the request was successful
  if response.status_code == 200:
      # Parse the JSON response
      user_info = response.json()
      return {
          "username": user_info['username'],
          "email": user_info['email']
      }
  else:
      # Print the error
      return {"error":f"Failed to fetch user information. Status Code: {response.status_code}, Response: {response.text}"}