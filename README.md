# Vend-O-Matic

A lightweight HTTP service that simulates a beverage vending machine. Built with Python and Django, this application exposes REST-style endpoints for coin insertion, inventory management, beverage purchases, and coin returns.

## Features

- Accepts US quarters, one coin per request.
- Each beverage costs two quarters.
- Maintains three beverage types, with five units of each initially available.
- Supports purchases with extra coins and returns unused quarters as change.
- Provides inventory information through HTTP endpoints.
- Handles insufficient funds and out-of-stock scenarios.
- Includes automated tests for business logic and HTTP API behavior.

## Technology Stack

- Python 3.11
- Django 5.2.19
- SQLite (Django's default local development database; not used for vending-machine state)
- Django Test Client for automated API testing

## Project Structure

```text
vend-o-matic/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── vending/
│   ├── migrations/
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── models.py
│   ├── admin.py
│   └── apps.py
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Prerequisites

- Python 3.11 or later
- pip

## Setup and Installation

### macOS / Linux

1. Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd vend-o-matic
```

2. Create a virtual environment:

```bash
python3 -m venv venv
```

3. Activate the virtual environment:

```bash
source venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Apply Django migrations:

```bash
python manage.py migrate
```

6. Start the development server:

```bash
python manage.py runserver
```

### Windows (PowerShell)

1. Clone the repository:

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd vend-o-matic
```

2. Create a virtual environment:

```powershell
python -m venv venv
```

3. Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Apply migrations:

```powershell
python manage.py migrate
```

6. Start the development server:

```powershell
python manage.py runserver
```

The service will be available at:

`http://127.0.0.1:8000/`

## API Documentation

All API requests use the `application/json` content type when a request body is required.

### 1. Insert a Coin

**Request**

```http
PUT /
Content-Type: application/json
```

Request body:

```json
{
  "coin": 1
}
```

**Successful response**

- Status: `204 No Content`
- Header: `X-Coins: 1`

Each request inserts one quarter.

Only the integer value `1` is accepted.

### 2. Return Coins

**Request**

```http
DELETE /
```

**Response**

- Status: `204 No Content`
- Header: `X-Coins: <number of coins returned>`

Returns all currently inserted coins and resets the coin balance.

### 3. Get All Inventory

**Request**

```http
GET /inventory
```

**Response**

- Status: `200 OK`

Example response:

```json
[5, 5, 5]
```

Returns the remaining quantities of all three beverage types in ID order.

### 4. Get Individual Item Inventory

**Request**

```http
GET /inventory/1
```

**Response**

- Status: `200 OK`

Example response:

```json
5
```

Returns the remaining quantity for the requested beverage ID.

### 5. Purchase a Beverage

**Request**

```http
PUT /inventory/1
```

No request body is required.

**Successful response**

- Status: `200 OK`
- Header: `X-Coins: <number of coins returned as change>`
- Header: `X-Inventory-Remaining: <remaining item quantity>`

Example response body:

```json
{
  "quantity": 1
}
```

One beverage is dispensed per successful transaction. Any quarters exceeding the purchase price are returned.

### 6. Out-of-Stock Scenario

**Request**

```http
PUT /inventory/1
```

**Response**

- Status: `404 Not Found`
- Header: `X-Coins: <number of coins accepted>`

Returned when the requested beverage is out of stock.

### 7. Insufficient Funds Scenario

**Request**

```http
PUT /inventory/1
```

**Response**

- Status: `403 Forbidden`
- Header: `X-Coins: 0 or 1`

Returned when the inserted coins are insufficient to purchase the requested beverage.

## Assumptions and Design Decisions

The assessment does not explicitly define every transaction-handling detail. The following assumptions were used:

1. **Coin denomination:** Each accepted coin represents one US quarter.
2. **Pricing:** Each beverage costs two quarters.
3. **Beverage identifiers:** The three beverages use IDs 1, 2, and 3 because specific names and identifiers were not provided.
4. **Insufficient funds:** When a purchase is attempted with fewer than two quarters, all inserted coins are returned and the balance is reset.
5. **Out of stock:** When a purchase is attempted for an unavailable beverage, all inserted coins are returned and the balance is reset.
6. **Successful purchase:** Exactly one beverage is dispensed per transaction. Any coins exceeding the purchase price are returned as change.
7. **Persistence:** Inventory and coin balance are maintained in memory and reset when the application restarts. Persistent storage was not specified in the assessment.
8. **Machine state:** A single shared vending-machine instance is used by the application.

## Running Tests

Run the automated test suite:

```bash
python manage.py test vending
```

The test suite covers:

- Initial inventory.
- Coin insertion and validation.
- Exact-payment and extra-coin purchases.
- Insufficient funds.
- Out-of-stock behavior.
- Manual coin returns.
- HTTP endpoint status codes.
- Response bodies and headers.
- Invalid request handling.
- Inventory updates through HTTP requests.

## Dependencies

Dependencies are listed in `requirements.txt`.

Install them using:

```bash
pip install -r requirements.txt
```

## Notes

This project is an implementation of the Vend-O-Matic take-home assessment. It uses Django to expose an HTTP API and does not include a frontend interface, as the assessment specifies HTTP-based testing.