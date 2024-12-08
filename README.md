# emissions-tracker

FastAPI-based backend service designed to fetch and aggregate carbon emissions data from multiple business facilities. The service uses Redis for caching and MongoDB for storing and querying emissions data. It supports date range filtering and provides efficient handling of missing or cached data to reduce database load and improve performance.

## Endpoints

### 1. Emissions Endpoint

To fetch emissions data for a given facility and date range, use the following endpoint:


**Example Request:**

http://127.0.0.1:8000/api/emissions/?start_date=2021-03-01&end_date=2022-03-30&business_facilities=GreenEat%20Changi


### Query Parameters:

- `start_date` (optional): The start date in the format `YYYY-MM-DD`.
- `end_date` (optional): The end date in the format `YYYY-MM-DD`.
- `business_facilities`: A list of business facility names to filter emissions data.

**Example:**
?start_date=2021-03-01&end_date=2022-03-30&business_facilities=GreenEat Changi

This will return aggregated emissions data for the `GreenEat Changi` facility from March 1, 2021, to March 30, 2022.

---

### 2. File Upload for CSV Data

The UI provides a functionality to upload a CSV file containing transaction data. This file will be processed and the data will be uploaded to the MongoDB database.

---

## Setup

### 1. Clone the Repository

Clone the repository to your local machine:

git clone <repository_url>
cd emissions-tracker

### Create a .env file or set the following environment variables before running the application:

## MongoDB settings
THis is a temporary user , you can set similar URI for mongodb atlas
MONGO_DETAILS = "mongodb+srv://sainivk565:nApRDjUAvYIiR1ut@cluster0.5kpc6rf.mongodb.net/?retryWrites=true&w=majority&tls=true&tlsAllowInvalidCertificates=true"
DB_NAME = "uc_task"
TRANSACTIONS_COLLECTION = "emissions"

## Redis settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379

## To start the application, run the following command:
bash start.sh
