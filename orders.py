"""
Moudle to import all orders or specific order from WooCommerce
"""
import concurrent.futures
from woocommerce import API
from datetime import datetime
from pymongo import MongoClient
from tqdm import tqdm
from dateutil import parser as dateparser

import config


wcapi = API(
    url=config.STORE_URL,
    consumer_key=config.CONSUMER_KEY,
    consumer_secret=config.CONSUMER_SECRET,
    version="wc/v3",
    timeout=120,
)

client = MongoClient(config.MONGO_URI)
db = client.test

max_order_per_page = 25


def import_all_orders(sort, from_date, to_date):
    """
    Import all orders between from_date and to_date

    params:
    sort: str - Sort orders ascending or descending.
    from_date: str - import orders submitted starting from this date
    to_date: str - import orders submitted untill this date

    returns: list of orders
    """
    after = datetime.fromisoformat(from_date)
    before = datetime.fromisoformat(to_date)

    page = 1
    initial_orders = wcapi.get(
        "orders",
        params={
            "per_page": max_order_per_page,
            "after": after.isoformat(),
            "before": before.isoformat(),
            "page": page,
            "order": sort,
        },
    )
    total_pages = initial_orders.headers.get("X-WP-TotalPages", 0)
    print(f"Total pages: {total_pages}\n")
    pages = range(1, int(total_pages) + 1)

    # use multi-threading to pull multiple orders concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_order = {
            executor.submit(get_orders, page, sort, after, before): page
            for page in pages
        }
        for future in tqdm(
            concurrent.futures.as_completed(future_to_order),
            total=int(total_pages),
            unit="page",
        ):
            try:
                orders = future.result()
            except:
                pass
            else:
                process_orders(orders)


def get_orders(page, sort, after, before):
    """Get orders on a specific page."""
    try:
        response = wcapi.get(
            "orders",
            params={
                "per_page": max_order_per_page,
                "after": after.isoformat(),
                "before": before.isoformat(),
                "page": page,
                "order": sort,
            },
        )
        if response.status_code == 200:
            order_detail = response.json()
            return order_detail
        else:
            print(f"Error status code {response.status_code} for page {page}")
    except Exception as e:
        print(f"Unexpected Error: {e}")
    return []


def process_orders(orders):
    """
    Process order to convert date and times to datetime objects
    and insert to MongoDB database
    """
    for order in orders:
        if not order.get("id", None):
            print("No order id skipping")
            continue

        date_fields = [
            "date_created",
            "date_created_gmt",
            "date_modified",
            "date_modified_gmt",
            "date_paid",
            "date_paid_gmt",
            "date_completed",
            "date_completed_gmt",
        ]
        for field in date_fields:
            if field not in order:
                continue
            str_date = order[field]
            if not str_date:
                continue
            order[field] = dateparser.isoparse(str_date)

        db[config.ORDER_COLLECTION].find_one_and_replace(
            filter={"id": order.get("id")}, replacement=order, upsert=True
        )


def get_order(id):
    """Get specific order specified by ID."""
    order = wcapi.get(f"orders/{id}").json()
    if not order.get("id", None):
        print("No order id skipping")
        return

    date_fields = [
        "date_created",
        "date_created_gmt",
        "date_modified",
        "date_modified_gmt",
        "date_paid",
        "date_paid_gmt",
        "date_completed",
        "date_completed_gmt",
    ]
    for field in date_fields:
        if field not in order:
            continue
        str_date = order[field]
        if not str_date:
            continue
        order[field] = dateparser.isoparse(str_date)

    db[config.CUSTOMER_COLLECTION].find_one_and_replace(
        filter={"id": order.get("id")}, replacement=order, upsert=True
    )
