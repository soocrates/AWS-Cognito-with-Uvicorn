from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from dotenv import load_dotenv
from typing import Optional
import requests
import os
from auth import is_authenticated

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
    if is_authenticated():
        return RedirectResponse(url="/whoami")
    if not code:
        raise HTTPException(status_code=400, detail="Code query parameter is missing")
    
    client_id = os.getenv('CLIENT_ID')
    redirect_uri = os.getenv('REDIRECT_URI')
    region = os.getenv('REGION')
    domain = os.getenv('HOSTED_UI_COGNITO_DOMAIN')
    
    token_endpoint = f"https://{domain}.auth.{region}.amazoncognito.com/oauth2/token"
    # Prepare and send request
    data = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': '',
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
      
@app.get("/whoami/")
async def get_user_name(request: Request, auth=Depends(is_authenticated)):
    global authenticated_user_info
    return {
        "Hello": authenticated_user_info["username"],
        "Email": authenticated_user_info["email"]
    }