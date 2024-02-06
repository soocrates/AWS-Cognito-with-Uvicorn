import os
import json
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
import jwt
from jwt import PyJWKClient

app = FastAPI()

COGNITO_DOMAIN = "sign-in-chatadex.auth.us-east-1.amazoncognito.com"
COGNITO_CLIENT_ID = "3hmj2km82pmptulvtu78rf8mst"
COGNITO_CLIENT_SECRET = "854o02nkpgt7qpjv726ut7u8qk9sl8h1vtdfomr9ucss0mlpt9j"
COGNITO_REDIRECT_URI = "me.sandbox.adex.ltd/"
COGNITO_REGION = "us-east-1"
COGNITO_USER_POOL_ID = "us-east-1_dRTHdC3jH"
SCOPES = "email+openid+phone+profile"

AUTH_URL = f"https://{COGNITO_DOMAIN}/login?client_id={COGNITO_CLIENT_ID}&response_type=code&scope={SCOPES}&redirect_uri=https%3A%2F%2F{COGNITO_REDIRECT_URI}%2F"
TOKEN_URL = f"https://{COGNITO_DOMAIN}/oauth2/token"
LOGOUT_URL = f"https://{COGNITO_DOMAIN}/logout"


async def get_cognito_jwt_secret() -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"

    async with httpx.AsyncClient() as client:
        response = await client.get(JWKS_URL)

    if response.status_code != 200:
        raise Exception("Failed to fetch JWKS from Cognito")

    jwks = response.json()
    for key_data in jwks["keys"]:
        if key_data["alg"] == "RS256" and key_data["use"] == "sig":
            key = jwk.construct(key_data)
            return key.to_pem().decode("utf-8")

    raise Exception("Failed to find a suitable public key in JWKS")


async def get_token(request: Request):
    token = request.query_params.get("token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required")
    return token

async def get_current_user(token: str = Depends(get_token)) -> str:
    JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    client = PyJWKClient(JWKS_URL)

    try:
        header = jwt.get_unverified_header(token)
        key = client.get_signing_key(header["kid"])
        public_key = key.key
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token claims")
    except jwt.JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


@app.get("/", response_class=HTMLResponse)
async def login():
    return f"""
    <html>
        <head>
            <title>Login</title>
        </head>
        <body>
            <a href="{AUTH_URL}">Login </a>
        </body>
    </html>
    """

@app.get("/callback")
async def callback(code: str):
    data = {
        "grant_type": "authorization_code",
        "client_id": COGNITO_CLIENT_ID,
        "client_secret":COGNITO_CLIENT_SECRET,
        "code": code,
        "redirect_uri": COGNITO_REDIRECT_URI,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
        }
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid code")
    token = response.json()

    return RedirectResponse(url=f"/chatbot?token={token['access_token']}")

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot(sub: str = Depends(get_current_user)):
    return f"""
    <html>
        <head>
            <title>Chatbot</title>
        </head>
        <body>
            <h1>Welcome, {sub}!</h1>
            <p>Here you can chat with the robot.</p>
        </body>
    </html>
    """

# Update the logout endpoint
@app.get("/logout")
async def logout(request: Request):
    token = request.query_params.get("token")
    return RedirectResponse(url=f"{LOGOUT_URL}?client_id={COGNITO_CLIENT_ID}&logout_uri={COGNITO_REDIRECT_URI}&token={token}")


# Run the app using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)