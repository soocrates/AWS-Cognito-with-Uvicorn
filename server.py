from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from typing import Optional
import requests
import os

app = FastAPI()
# Load the environment variables from .env file
load_dotenv()

# A simple root route
@app.get("/")
def read_root():
    return {"Hello": "World"}

# A route that returns HTML content
@app.get("/html", response_class=HTMLResponse)
def read_html():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Hello, world!</h1>
        </body>
    </html>
    """
@app.get("/authenticated")
def read_authenticated(code: Optional[str] = None):
    if not code:
        raise HTTPException(status_code=400, detail="Code query parameter is missing")
    else:
        client_id = os.getenv('CLIENT_ID')
        userpoolid = os.getenv('USERPOOL_ID')
        redirect_uri = os.getenv('REDIRECT_URI')
        region = os.getenv('REGION')
        client_secret = ''
        
        cognito_idp_url = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}/.well-known/openid-configuration"
        cognito_idp_response = requests.get(cognito_idp_url)

        if cognito_idp_response.status_code == 200:
            openid_config = cognito_idp_response.json()
            token_endpoint = openid_config.get("token_endpoint")
                # Prepare and send request
            data = {
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'redirect_uri': redirect_uri
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(token_endpoint, data=data, headers=headers)
            # Check response status
            if response.status_code == 200:
                response_data = response.json()
                if not response_data["token_type"] == 'Bearer':
                    # Parse the JSON response
                    response.set_cookie(key="id_token", value=response_data["id_token"], httponly=True, secure=True)
                    response.set_cookie(key="access_token", value=response_data["access_token"], httponly=True, secure=True)
                    response.set_cookie(key="refresh_token", value=response_data["refresh_token"], httponly=True, secure=True)
                    response.set_cookie(key="expires_in", value=response_data["expires_in"], httponly=True, secure=True)

                    return { "response": response_data, "code": code}
                else:
                    raise HTTPException(status_code=403, detail="Wrong authentication method") 
            else:
                return {
                    "message": "Failed to retrieve tokens",
                    "Status Code": response.status_code,
                    "Response": response.text
                }
        else:
            return {
                "Status Code": cognito_idp_response.status_code,
                "Response": cognito_idp_response.text
            }
            
@app.get("/authenticated/{username}", Depends())
def get_user_name():
    return {"Hello": "World"}