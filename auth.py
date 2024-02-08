from fastapi import HTTPException, Request
from signature import signature_verification
from userinfo import retrive_user_information


authenticated_user_info = {}
async def is_authenticated(request: Request):
    # Extract the access_token from the cookie in the request
    
    global authenticated_user_info  # Declare the global variable
    
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(status_code=401, detail="Token is missing. Login Again")

    # Verify the signature of the access token
    verification_result = await signature_verification(access_token)
    userinfo_result = retrive_user_information(access_token)
    if "message" in verification_result and verification_result["message"] == "Signature Verified!":
        if verification_result["username"] == userinfo_result["username"]:
            # Store the user info in the global variable
            authenticated_user_info = {
                "email": userinfo_result["email"],
                "username": userinfo_result["username"],
                "expiration_time": verification_result["expiration_time"]
            }
            # The token is valid
            return True
        else:
            return None
            # raise HTTPException(status_code=403, detail="Username Mismatch. Please Try Again")
            
    elif "error" in verification_result:
        detail = verification_result["error"]
        # Passing status code 302  for passing errors of previous function
        raise HTTPException(status_code=302, detail=detail)
    else:
        # The token is not valid
        detail = verification_result.get("error", "Authentication failed")
        raise HTTPException(status_code=401, detail=detail)