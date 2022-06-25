"""
Module to import all customers or specific customer from WooCommerce
"""
import concurrent.futures
from woocommerce import API
from tqdm import tqdm
from pymongo import MongoClient
from dateutil import parser as dateparser

import config
from orders import MAX_THREADS


wcapi = API(
    url=config.STORE_URL,
    consumer_key=config.CONSUMER_KEY,
    consumer_secret=config.CONSUMER_SECRET,
    version="wc/v3",
    timeout=120,
)

client = MongoClient(config.MONGO_URI)
db = client.test

MAX_THREADS = 10
max_customer_per_page = 100


def import_all_customers(sort, from_date, to_date):
    """
    Import all customers having specific role

    params:
    sort: str - Sort orders ascending or descending.
    from_date: str - import orders submitted starting from this date
    to_date: str - import orders submitted untill this date

    returns: list of customers
    """
    page = 1
    initial_customers = wcapi.get(
        "customers",
        params={
            "per_page": max_customer_per_page,
            "page": page,
            "role": "seller",
        },
    )
    total_pages = initial_customers.headers.get("X-WP-TotalPages", 0)
    print(f"Total pages: {total_pages}\n")
    pages = range(1, int(total_pages) + 1)

    # use multi-threading to pull multiple customers concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_customer = {
            executor.submit(get_customers, page, sort): page for page in pages
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_customer),
            total=int(total_pages),
            unit="page",
        ):
            try:
                customers = future.result()
            except:
                pass
            else:
                process_customers(customers, from_date, to_date)


def get_customers(page, sort):
    """Get customers on a specific page."""
    try:
        response = wcapi.get(
            "customers",
            params={
                "per_page": max_customer_per_page,
                "page": page,
                "order": sort,
                "role": "seller",
            },
        )
        if response.status_code == 200:
            customers = response.json()
            return customers
        else:
            print(f"Error status code {response.status_code} for page {page}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return []


def process_customers(customers, from_date, to_date):
    """
    Process customer to convert date and times to datetime objects
    and import customers created between the specified date
    """
    for customer in customers:
        if not customer.get("id", None):
            print("No customer id skipping")
            continue

        if from_date <= customer["date_created"] <= to_date:
            date_fields = [
                "date_created",
                "date_created_gmt",
                "date_modified",
                "date_modified_gmt",
            ]
            for field in date_fields:
                if field not in customer:
                    continue
                str_date = customer[field]
                if not str_date:
                    continue
                customer[field] = dateparser.isoparse(str_date)

            db[config.CUSTOMER_COLLECTION].find_one_and_replace(
                filter={"id": customer.get("id")}, replacement=customer, upsert=True
            )


def get_customer(id):
    """Get specific customer specified by ID."""
    customer = wcapi.get(f"customers/{id}").json()
    if not customer.get("id", None):
        print("No customer id skipping")
        return

    date_fields = [
        "date_created",
        "date_created_gmt",
        "date_modified",
        "date_modified_gmt",
    ]
    for field in date_fields:
        if field not in customer:
            continue
        str_date = customer[field]
        if not str_date:
            continue
        customer[field] = dateparser.isoparse(str_date)

    db[config.CUSTOMER_COLLECTION].find_one_and_replace(
        filter={"id": customer.get("id")}, replacement=customer, upsert=True
    )
