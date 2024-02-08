from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
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
    
    client_id = os.getenv('CLIENT_ID')
    userpoolid = os.getenv('USERPOOL_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    region = os.getenv('REGION')
    client_secret = ''
    
    cognito_idp_url = f"https://cognito-idp.{region}.amazonaws.com/{userpoolid}/.well-known/openid-configuration"
    cognito_idp_response = requests.get(cognito_idp_url)

    if cognito_idp_response.status_code != 200:
        return JSONResponse(status_code=cognito_idp_response.status_code, content={"message": "Failed to load OpenID configuration"})

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
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response_token = requests.post(token_endpoint, data=data, headers=headers)

    if response_token.status_code == 200:
        response_data = response_token.json()
        if response_data["token_type"] == 'Bearer':
            content = {"response": response_data, "code": code}
            response = JSONResponse(content=content)
            # Set cookies here
            response.set_cookie(key="id_token", value=response_data["id_token"], max_age= response_data["expires_in"], httponly=True, secure=True, samesite='Lax')
            response.set_cookie(key="access_token", value=response_data["access_token"], max_age= response_data["expires_in"], httponly=True, secure=True, samesite='Lax')
            response.set_cookie(key="refresh_token", value=response_data["refresh_token"], max_age= 60 * 60 * 24 * 7, httponly=True, secure=True, samesite='Lax')
            response.set_cookie(key="code", value=code, max_age= response_data["expires_in"], httponly=True, secure=True, samesite='Lax')
            return response
        else:
            raise HTTPException(status_code=403, detail="Wrong authentication method")
    else:
        return JSONResponse(status_code=response_token.status_code, content={"message": "Failed to retrieve tokens"})
      
@app.get("/authenticated/{username}")
def get_user_name():
    return {"Hello": "World"}