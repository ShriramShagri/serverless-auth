# Serverless WebApp

A demo webapp for token management which can be deployed using aws lambda functions.

## Requirements

* AWS account(Free Tier is available)
* RedisLabs Cloud database(Free tier available)
* AWS CLI installed

## Setup

* Get or create new `AWS Access Key ID` and `AWS Secret Access Key` from **Profile --> My Security Credentials** from AWS Website.

* Run `aws configure` and add these details along with `Default region name` (ex: `us-east-2`)

    ```bash
    $ aws configure
    AWS Access Key ID [None]:Your AWS Access Key ID
    AWS Secret Access Key [None]:Your AWS Secret Access Key
    Default region name [None]: Default region name
    Default output format [None]:
    $
    ```

* Clone the repository to a folder

    ```bash
    git clone 
    ```

* `cd` into folder and create virtual environment and activate.

    ```bash
    python3 -m venv env
    . env/bin/activate
    ```

* Install all required modules

    ```bash
    pip3 install -r requirements.txt
    ```

* Get RedisLab Cloud database credentials (host:port and password)

* Update the details of database in [src/constants.py](src/constants.py) file.

* To test and run server locally run

    ```bash
    chalice local
    ```

* If it works fine then deploy on AWS lambda using
  
    ```bash
    chalice deploy
    ```

## Docs

* [Chalice Documentation and tutorial](https://aws.github.io/chalice/)

* [Redis Python Documentation](https://redis-py.readthedocs.io/)

## Routes

* `{{url}}/auth` home route for testing
  * GET Request
  * Include `Authorization : token` in headers
  * Reply:

      ```json
      {
          "result": "Hello *username",
          "status": "SUCCESS",
          "status_code": 1000
      }
      ```

* `{{url}}/auth/signin` Signin route
  * POST Request
  * Body:

      ```json
      {
          "username" : "username",
          "password" : "password"
      }
      ```
  
  * Reply (includes token valid for 1 minute):

      ```json
      {
          "result": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IlNoYWdyaSIsInNhbHQiOiIwOTNlZGNlMTg3OTQzYmU1MDllZWQzZmQ3MGE0ODBhMjYwNWY4OTAxZjRiYWEwNzYzYjU0OTlmMzA2NmYzYmM0OTcwZTBjMTllMjU2YTI5ODY0NGE1ZGEwYjcyNTA5MDlhYjljNDYzYzE1OTFiNmQxNmNmNGY5NDAyOTJlYTAwYiIsImV4cCI6MTYxOTYwNzI0OX0.R_U90dOTSOLgHjVHGNqoPTir1w-E1coY9jDNr5fxo20",
          "status": "SUCCESS",
          "status_code": 1000
      }
      ```

* `{{url}}/auth/signup` Signup new user
  * POST Request
  * Body:

      ```json
      {
          "username" : "username",
          "password" : "password"
      }
      ```
  
  * Reply:

      ```json
      {
          "result": "",
          "status": "SUCCESS",
          "status_code": 1000
      }
      ```

* `{{url}}/auth/password` Change password
  * POST Request
  * Include `Authorization : token` in headers
  * Body:

      ```json
      {
          "password" : "new password"
      }
      ```
  
  * Reply:

      ```json
      {
          "result": "",
          "status": "SUCCESS",
          "status_code": 1000
      }
      ```
