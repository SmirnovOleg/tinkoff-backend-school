# Crypto Market API

REST-API service for simplified cryptocurrency trading.

API endpoints:

```
- POST /users/
  - login
  
- GET  /users/{login}/balance

- GET  /users/{login}/portfolio

- GET  /users/{login}/history?page={page_num}

- GET  /cryptocurrencies/{cypto_name}/prices

- POST /cryptocurrencies
  - crypto_name
  - sale-price
  - purchase_price
  
- PUT  /cryptocurrencies/buy
  - utc_datetime
  - login
  - crypto_name
  - amount
  
- PUT  /cryptocurrencies/sell
  - utc_datetime
  - login
  - crypto_name
  - amount
```

### Create venv:

    make venv

### Run server:

    make up

### Run tests:

    make test

### Run linters:

    make lint

### Run formatters:

    make format
    
    