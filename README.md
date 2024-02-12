# 🚀 FastAPI Authentication with AWS Cognito 🚀

This project is a demonstration 📚 of implementing a secure authentication system in a FastAPI application using AWS Cognito. It covers the OAuth2 authentication flow, including token verification, user information retrieval, and secure session management through cookies 🍪. This setup ensures that certain routes are protected and only accessible to authenticated users 🔐.

## Features 🌟

- **OAuth2 Authentication Flow** 🛂: Integration with AWS Cognito to manage user authentication.
- **Token Verification** 🔑: Secure verification of JWT tokens using AWS Cognito's JWKS endpoint.
- **User Information Retrieval** 🧑‍💻: Fetching authenticated user details from AWS Cognito.
- **Secure Cookie Management** 🍪: Handling session tokens securely through HTTPOnly cookies.
- **Protected Routes** 🚧: Ensuring some parts of the application are accessible only to authenticated users.

## Prerequisites 📋

To use this project, you'll need:

- Python 3.7+ installed on your machine 🐍.
- An AWS account and a Cognito User Pool set up ☁️.
- A `.env` file in the project root with AWS Cognito details 📁.

## Installation 💾

1. **Clone the Repository** 📥

    Start by cloning this repository to your local machine:

    ```bash
    git clone https://github.com/soocrates/AWS-Cognito-with-Uvicorn.git
    cd your-project-directory
    ```

2. **Install Dependencies** 📦

    Install the necessary Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration ⚙️

Create a `.env` file in the root directory of your project with the following content.
* Replacing placeholders with your actual AWS Cognito details:
    
        CLIENT_ID=your_cognito_client_id_here
        USERPOOL_ID=your_userpool_id_here
        REGION=your_aws_region_here
        HOSTED_UI_COGNITO_DOMAIN=your_cognito_domain_here
        REDIRECT_URI=your_redirect_uri_after_login

These details are used to configure the authentication flow with AWS Cognito in your application.

## Running the Application 🏃‍♂️

* To run the FastAPI application, execute:

    ```bash
    uvicorn server:app --reload
    OR,
    uvicorn server:app --reload --host 127.0.0.1 --port 8000
    ```
* This command starts a local server on http://localhost:8000. You can access the API endpoints as defined in your application.

## Endpoints Overview  🗺️
* `GET /:` The root route returns a simple hello world message 🌍..
* `GET /authenticated:` Handles the OAuth2 callback, exchanges the code for tokens, and sets up session cookies 🔄.
* `GET /whoami/:` A protected route that displays the authenticated user's username and email 📧..
* `GET /protected-route:` Another example of a protected route, accessible only to authenticated users  🔒.
* `GET /logout:` Clears the session cookies, effectively logging the user out 🔚.

## Contributing 🤝
Contributions to improve the project are welcome. Please follow these steps:
* Fork the repository.🍴.
    ``` 
    Create your feature branch (git checkout -b feature/AmazingFeature).
    Commit your changes (git commit -m 'Add some AmazingFeature').
    Push to the branch (git push origin feature/AmazingFeature).
    Open a pull request. ```
## Important 📌
If you are using web server like nginx, take a look at your proxy header configurations, Increase or decrease your buffers according to your Application Need
 * #### Nginx Configuration Snippet 📝
     ```       
    # Maximum allowed size for client request bodies 16 MB
    client_max_body_size 16M; 
    # Adjust buffer and timeout settings for the server
    large_client_header_buffers 16 32k;
    proxy_buffer_size 16k;
    proxy_buffers 8 16k;
    proxy_busy_buffers_size 16k;
        