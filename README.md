# FSND-Capstone We_Donors
  This app aims to provide a trustworthy donation platform where donors can contribute to cases that serve their community, this app could be customized further to meet special needs (rescue animals, crisis). The roles available are:
    - administrators with the permission to create, delete cases and to view all donations. 
    - donors with permission to make donations which may update the value of the subject case.


# Installing Dependencies
 Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

# PIP Dependencies
Once you have your virtual environment setup and running, install dependencies by naviging to the project directory and running:
    
    pip install -r requirements.txt

This will install all of the required packages addeded within the `requirements.txt` file.

# Database

to create database use below command
createdb -U [username] we_donors

to create test database use below command
createdb -U [username] we_donors_test

# running the server
to run the server locally, navigate to project directory and use below commands
    
    export FLASK_APP=flaskr
    export FLASK_ENV=development

for windows users use
    
    set FLASK_APP=flaskr
    set FLASK_ENV=development

and then run the server    
    flask run

# running the tests
to run the tests, navigate to project directory and use below commands
python test.py


APIs:

GET '/cases'
- Retrieves all cases, this endpoint does not require any permission
- Parameters: 
  none  
- Sample: http://127.0.0.1:5000/cases
- Returns: 'cases' object which contains a list of cases objects - each contains number, date, id, issuer, number, paid, total_amount and a list of object services where each service consists of amount, case_id, quantity 
{
  "cases": [
    {
      "date": "08/08/2020 17:43:57",
      "id": 1,
      "issuer": "Go87",
      "number": "tryfme",
      "paid": true,
      "services": [
        {
          "amount": 20.0,
          "case_id": 1,
          "quantity": 10
        },
        {
          "amount": 200.0,
          "case_id": 1,
          "quantity": 1
        }
      ],
      "total_amount": 230.0
    },
    {
      "date": "08/08/2020 19:07:53",
      "id": 6,
      "issuer": "Godd",
      "number": "tryfme",
      "paid": null,
      "services": [
        {
          "amount": 20.0,
          "case_id": 6,
          "quantity": 10
        },
        {
          "amount": 200.0,
          "case_id": 6,
          "quantity": 1
        }
      ],
      "total_amount": 230.0
    },
    ...
  ],
  "success": true
}

GET '/donations'
- Retrieves all donations, the endpoint requires administrator permission
- Parameters: 
  none  
- Sample: http://127.0.0.1:5000/donations
- Returns: 'donations' object which consists of a list of donations objects - each one contains case_id, donor_id, paid_amount 
{
  "donations": [
    {
      "case_id": 1,
      "donor_id": null,
      "paid_amount": 230.0
    },
    {
      "case_id": 1,
      "donor_id": null,
      "paid_amount": 230.0
    }
  ],
  "success": true
}

GET '/cases/<case_id>'
- Fetches particular case by id, this endpoint does not require any permission
- Parameters: 
  Request Arguments: case_id of type integer
- Sample: http://127.0.0.1:5000/cases/1
- Returns: 'cases' object which contains a list with specific case object which contains number, date, id, issuer, number, paid, total_amount and a list of object services where each service consists of amount, case_id, quantity 
{
  "cases": {
    "date": "08/08/2020 17:43:57",
    "id": 1,
    "issuer": "Go87",
    "number": "tryfme",
    "paid": true,
    "services": [
      {
        "amount": 20.0,
        "case_id": 1,
        "quantity": 10
      },
      {
        "amount": 200.0,
        "case_id": 1,
        "quantity": 1
      }
    ],
    "total_amount": 230.0
  },
  "success": true
}

POST '/cases/<case_id>'
- Adds a new case using given data, this endpoint requires administrator permission
- Parameters: 
    Request Body Parameters:
    - number of type string
    - issuer of type string
    - total_amount of type float
    - list of services [optional], each service is an object that should include:
        - description of type string
        - amount of type float
        - quantity  of type integer
- Sample: http://127.0.0.1:5000/cases
    request body:
    {
    "issuer": "Gd",
    "services": [{"description":"test1", "amount":20,"quantity":10},{"description":"test3","amount":200,"quantity":1}],
    "number": "tryfme",
    "total_amount": 230.0
    }
- Returns: newly inserted case_id

PATCH '/cases/<case_id>'
- Adds a new donation linked with given case id, this endpoint requires donor permission
- Parameters: 
    Request ARGUMENT: CASE_ID OF TYPE INTEGER
    Request Body Parameters: object of key:value pair where key is amount and value is of float type
- Sample: http://127.0.0.1:5000/cases/1
    request body:
    {"amount": 230}
- Returns: newly inserted newly added donation_id


DELETE '/cases/<case_id>'
- Adds a new donation linked with given case id, this endpoint requires administrator permission
- Parameters: 
    Request ARGUMENT: CASE_ID OF TYPE INTEGER
- Sample: http://127.0.0.1:5000/cases/1
- Returns: delete case_id

