from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.responses import JSONResponse, RedirectResponse
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

@app.get("/authenticated")
def read_authenticated(code: Optional[str] = None):
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
            content = {"response": response_data}
            response = JSONResponse(content=content)
            # Set cookies here
            response.set_cookie(key="id_token", value=response_data["id_token"], max_age= response_data["expires_in"], httponly=True, secure=True, samesite='Lax')
            response.set_cookie(key="access_token", value=response_data["access_token"], max_age= response_data["expires_in"], httponly=True, secure=True, samesite='Lax')
            response.set_cookie(key="refresh_token", value=response_data["refresh_token"], max_age= 60 * 60 * 24 * 7, httponly=True, secure=True, samesite='Lax')
            return RedirectResponse(url="/whoami/", status_code=303)
        else:
            raise HTTPException(status_code=403, detail="Wrong authentication method")
    else:
        return JSONResponse(status_code=response_token.status_code, content={"message": "Failed to retrieve tokens"})
      
@app.get("/whoami/")
async def get_user_name(request: Request, auth=Depends(is_authenticated)):
    _, user_info = auth  # Unpack the tuple returned by is_authenticated
    return {
        "Hello": user_info["username"],
        "Email": user_info["email"]
    }
@app.get("/protected-route")
async def protected_route(request: Request, auth=Depends(is_authenticated)):
    # If the code reaches here, the user is authenticated
    return {"message": "You are accessing a protected route."}