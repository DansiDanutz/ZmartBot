# KuCoin API Research and Testing

## Exchange Broker Introduction

Exchange Broker (also called Non-Disclosed Broker) is a type of brokerage services with functional flexibilities and client-management powers. As an Exchange Broker, your clients are unknown to KuCoin, and you provide all customer registration requirements, funding, customer service and marketing.

Exchange broker program provides a variety of API services, including but not limited to:
- Creating unlimited sub-accounts
- Deleting sub-accounts  
- Creating API Keys for sub-accounts
- Querying sub-account rebate records
- The API key of the sub-account can be used to place orders, view account assets, deposit/withdrawal funds, etc.

Typical clients suitable for the Exchange broker program include exchanges, wallets, cryptocurrency payment service providers, custodial or non-custodial trading platforms, aggregation trading platforms, etc.

**Important Note**: In the broker account(s) system, the broker Special Account (Sub-account) has similar attributes to the "main account" of an ordinary account, and therefore the relevant functions of the main account in the ordinary API interface can be used for broker Special Account (Sub-account) too, except for withdrawal and KCS deduction.

## User's Broker Credentials

**Broker Information:**
- C-BROKER-NAME: KRYPTOSTACKMASTER
- KC-API-PARTNER: KRYPTOSTACK_ND
- KC-API-PARTNER-SECRETKEY: 0c8b0cb9-58f5-4d0d-9c73-b7bde5110cc1

**API Keys (ZmartBot):**
- API Name: ZmartBot
- Key: 68888bce1cad950001b6966d
- Secret: ba4de6f6-2fb5-4b32-8a4c-12b1f3eb045a
- Passphrase: Danutz1981.
- Usage: API-Based Trading
- Restrictions: General, Futures Trading, Spot Trading, KuCoin Earn, Allow Flexible Transfers, Margin Trading
- IP Restrictions: Unrestricted




## KuCoin Broker Fast API Service (from Google Doc)

### 1. Introduction
KuCoin is launching the Fast API Service which allows broker users to connect to the broker's website/app via KuCoin OAuth2 login, an one-click authorization linked to third-party applications. The significant improvement with Fast API service is to generate enhanced security of the trading and simplify the way to connect KuCoin and Broker.

**Key Features:**
- No extra passphrase or API key (version3) is required to be manually binded with the broker's bot
- The OAuth connection will automatically create an API key and automatically connect to the broker
- The key has default permissions with spot trading, futures trading, as well as getting access to KuCoin Earn

### 2. Preparation before Integration
To utilize the KuCoin Fast API Service, Broker partners need to prepare the below three parts and submit from this form:

1. **Broker's full IP list** for requesting Fast API Service - This is the IP that the Broker server requests to our KuCoin fast api service server
2. **Broker's full IP list for trading** 
3. **Redirect URL**

Once the broker provides the above three, KuCoin will send the broker's unique **client_id**

### 3. Fast API Service
Broker users can use KuCoin OAuth login to authorize brokers obtaining their trading and reading general information.


### 4. OpenAPI Demo

**URL:** https://www.kucoin.com/_oauth/resource/ucenter/outer/api-key/add
**Method:** POST
**Content-Type:** application/json
**Header:** "Authorization":"bearer {token}"
**Parameter:** no parameter needed

**Response:**
```json
{
    "success": true,
    "code": "200",
    "msg": "success",
    "retry": false,
    "data": {
        "apiName": "",
        "apiKey": "",
        "secret": "",
        "passphrase": "",
        "brokerId": "",
        "authGroup": "API_COMMON,API_FUTURES,API_SPOT,API_EARN,API_TRANSFER,API_MARGIN",
        "ipWhiteList": ""
    }
}
```

**Errors:**
1. Repeated apiName
2. The number of user's apiKey reaches to the maximum level

### 5. Authorization Code Mode

KuCoin offers authorization code mode only. With authorization, the broker provides client_secret to get authorization code, access token and refresh token can be retrieved based on authorization codes. Broker saves keys and interacts with KuCoin OAuth2.0 server.

The authorization flow involves:
- User initiates authorization
- API Broker handles the process
- KuCoin returns authorization code
- Login account and confirm authorization


### 6. Use of Token

#### 6.1 Differences between tokens
After the broker calls the token exchange endpoint through authorization code, there will be two types of tokens:
- **access token**: Used for the broker to call KuCoin OpenAPI endpoint
- **refresh token**: Used for obtaining a new access token when the previous one expires

#### 6.2 How to use tokens
After the broker completes the authorization and obtains the token, it will be able to call the KuCoin OpenAPI endpoint through the access token. When requesting, broker needs to carry the following information in the request header:

| Header Parameters | Required | Descriptions |
|------------------|----------|--------------|
| Authorization | Yes | Fill in the access token as bearer to this field |

#### 6.3 Token validity
- **access token**: Valid within 1 hour
- **refresh token**: Valid within 3 days

If the access token expires, the endpoint will no longer be accessible. If the refresh token is still within the valid period, the broker needs to call the refresh token endpoint to obtain a new pair of access token and refresh token.


### 7. OAuth Controller API Design

#### 7.1 OAuth Login Page
**URL:** http://www.kucoin.com/oauth?response_type=code&client_id=XXXX&redirect_uri=XXX&scope=OAUTH_CREATE_API&state=123

**Method:** GET

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| Response Type | Yes | Please use the authorization_code mode |
| Client_id | Yes | Unique identity of the broker |
| Redirect_url | Yes | Broker website |
| Scope | Yes | Scope of access_token |
| State | No | Brokers can determine what you need here. But this is a compulsory field. You can put your system's user ID here |

**Response:**
```json
{
    "success": true,
    "code": "668*********C711",
    "msg": "success",
    "retry": false,
    "data": null,
    "state": XXX
}
```

**Tips:** please don't encode the redirect URL.

#### 7.2 Request A Token
**URL:** https://www.kucoin.com/_oauth/access-token?grant_type=authorization_code&code=xxxxxxxxxx&redirect_uri=https://www.xxxxxxxxxxxxx.com&client_id=xxxxxxxxx

**Method:** GET

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| Grant_type | Yes | grant_type=authorization_code |
| Code | Yes | |
| Redirect_url | Yes | |
| Client_id | Yes | Unique identity of the broker |

**Response:**
```json
{
    "access_token":"", //access token received from user authorization
    "token_type":"bearer", //token type, extension point to facilitate the addition of more secure tokens in the future
    "expires_in":3600, //token expiration time, in seconds
    "refresh_token":"", //token used to obtain a new access token after the access token expires
    "scope": ["", ""] //scope of permissions for the access token
}
```

#### 7.3 Refresh A Token
**URL:** https://www.kucoin.com/_oauth/refresh-token

**Method:** POST

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| Grant_type | Yes | authorization_code |
| Refresh_token | Yes | Token used to refresh the authentication |
| Scope | Yes | |

**Response:**
```json
{
    "access_token":"", //token used to access resources
    "token_type":"bearer", //token type, an extension point to facilitate the addition of more secure tokens in the future, such as MAC (Message Authentication Code). Bearer indicates a token that does not contain any information
    "expires_in":3600, //token expiration time, in seconds
    "refresh_token":"", //token used to obtain a new access token after the access token expires
    "scope": ["OAUTH_CREATE_API"] //scope of permissions for the access token
}
```


## KuCoin V3 Futures API Information

### Authentication (V3)
**Headers Required:**
- KC-API-KEY: The API key as a string
- KC-API-SIGN: The base 64-encoded signature
- KC-API-TIMESTAMP: A timestamp for your request (milliseconds)
- KC-API-PASSPHRASE: The passphrase encrypted with HMAC-sha256 via API-Secret and base64 encoded
- KC-API-KEY-VERSION: "2" (for current version)
- Content-Type: application/json

### Futures Order Placement Endpoint
**URL:** https://api-futures.kucoin.com/api/v1/orders
**Method:** POST

**Required Parameters:**
- clientOid: Unique order ID (max 40 chars, UUID format)
- side: "buy" or "sell"
- symbol: Contract symbol (e.g., "XBTUSDTM")
- type: "limit" or "market" (default: "limit")

**Optional Parameters:**
- leverage: Order leverage (for isolated margin)
- price: Operating price (required for limit orders)
- size: Order size in lots (choose one: size, qty, or valueQty)
- qty: Order size in base currency
- valueQty: Order size in value (USDT/USDC)
- marginMode: "ISOLATED" or "CROSS" (default: "ISOLATED")
- timeInForce: "GTC" or "IOC" (default: "GTC")
- reduceOnly: true/false (default: false)
- closeOrder: true/false (default: false)
- postOnly: true/false (default: false)
- hidden: true/false (default: false)
- iceberg: true/false (default: false)
- stop: "down" or "up" (for stop orders)
- stopPrice: Stop price (required if stop is used)
- stopPriceType: "TP", "IP", or "MP" (required if stop is used)

**Example Request:**
```json
{
    "clientOid": "5c52e11203aa677f33e493fb",
    "side": "buy",
    "symbol": "XBTUSDTM",
    "leverage": 3,
    "type": "limit",
    "remark": "order remarks",
    "reduceOnly": false,
    "marginMode": "ISOLATED",
    "price": "0.1",
    "size": 1,
    "timeInForce": "GTC"
}
```

### Limits
- Maximum limit orders per contract: 100 per account
- Maximum stop orders per contract: 200 per account


## API Broker Instructions

### Required Headers for Broker API
When using the API Broker functionality, the following additional headers must be included:

- **KC-API-PARTNER**: partner (provided by KuCoin)
- **KC-API-PARTNER-SIGN**: The base64-encoded signature
- **KC-BROKER-NAME**: broker-name (provided by KuCoin)
- **KC-API-PARTNER-VERIFY**: true (strongly recommended)

### Broker Signing Process
For the **KC-API-PARTNER-SIGN** header:
1. Use broker-key to encrypt the prehash string: `timestamp + partner + apiKey` with sha256 HMAC
2. Use base64-encode to encrypt the result from step 1

**Important Notes:**
- The timestamp value is the same as the KC-API-TIMESTAMP header
- The partner value is the same as the KC-API-PARTNER header
- The apiKey value is the same as KC-API-KEY

### User's Broker Configuration
Based on the provided credentials:
- **broker-name**: KRYPTOSTACKMASTER
- **partner**: KRYPTOSTACK_ND
- **broker-key**: 0c8b0cb9-58f5-4d0d-9c73-b7bde5110cc1

### Verification
To check if broker configuration is successful:
- **For Spot**: Query order interface `GET /api/v1/orders/{orderId}` - if returned tags are not empty, config is successful
- **For Futures**: Query order interface `GET /api/v1/orders/{order-id}?clientOid={client-order-id}` - if returned tags are not empty, config is successful

### Error Handling
- If KC-API-PARTNER-VERIFY is not added: KC-API-PARTNER-SIGN failures won't cause errors, but broker info won't be carried
- If KC-API-PARTNER-VERIFY is true: Any KC-API-PARTNER-SIGN failure will return error `{"code":"400201","msg":"Invalid KC-API-PARTNER-SIGN"}`


## API Key Upgrade Information

### V3 API Key Requirement
**Important**: As of July 2024, KuCoin has completely migrated from v2 to v3 API keys. All v2 API keys were invalidated between July 1-10, 2024.

### Key Points:
- All API implementations must use v3 API keys
- The upgrade is compatible and doesn't require code changes
- Only requires creating new v3 API keys and replacing old v2 keys
- The provided API keys are v3 compatible (confirmed by successful testing)

### Implementation Notes:
- KC-API-KEY-VERSION header must be set to "2" (this is the version identifier for v3 API)
- Authentication process remains the same as documented
- All endpoints and functionality are preserved in v3

