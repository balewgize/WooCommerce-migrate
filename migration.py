"""
Command-line interface for the script
"""
import click
import datetime
import customers, orders


@click.group()
def cli():
    """
    A command-line tool to migrate orders and customers from WooCommerce
    to MongoDB database.
    """
    pass


@click.command("orders")
@click.option(
    "--id",
    "-i",
    type=click.INT,
    help="ID of specific order to be imported.",
)
@click.option(
    "--sort",
    "-s",
    help="Order sort attribute ascending (asc) or descending (desc).",
    default="asc",
)
@click.option("--after", "-a", help="ISO datetime to import orders after (FROM)")
@click.option("--before", "-b", help="ISO datetime to import orders before (TO)")
@click.option(
    "--days",
    "-d",
    type=click.INT,
    help="Import orders created in the past X days (default=0 today)",
    default=0,
)
@click.option(
    "--hours",
    "-h",
    type=click.INT,
    help="Import orders created in the past X hours (default=1 hour)",
    default=1,
)
def import_orders(id, sort, after, before, days, hours):
    """
    Import all orders created between a datetime range or specific order
    """
    if id:
        print(f"Importing specific order with ID {id}")
        orders.get_order(id)
        return

    if sort:
        if sort.startswith("asc"):
            sort = "asc"
        elif sort.startswith("desc"):
            sort = "desc"
        else:
            sort = "asc"

    if after and before:
        print(
            f"Importing all orders created after '{after}' and before '{before}' sorted '{sort}'...\n"
        )
        orders.import_all_orders(sort, after, before)
    else:
        current_time = datetime.datetime.now()
        today = datetime.date.today()
        if days > 0:
            # user has provided days argument
            start_day = today - datetime.timedelta(days=days)
        else:
            # default is today
            start_day = today

        if start_day != today:
            after = f'{str(start_day)}T{current_time.strftime("%H:%M:%S")}.000'
        else:
            if hours > 1:
                # hours argument provided
                start_time = current_time - datetime.timedelta(seconds=hours * 3600)
            else:
                # last 1 hour
                start_time = current_time - datetime.timedelta(seconds=3600)

            after = f'{start_time.strftime("%Y-%m-%dT%H:%M:%S")}.000'

        before = f'{current_time.strftime("%Y-%m-%dT%H:%M:%S")}.000'
        print(
            f"Importing all orders created after '{after}' and before '{before}' sorted '{sort}'...\n"
        )
        orders.import_all_orders(sort, after, before)


@click.command("customers")
@click.option(
    "--id",
    "-i",
    type=click.INT,
    help="ID of specific customer to be imported.",
)
@click.option(
    "--sort",
    "-s",
    help="Customer sort attribute ascending (asc) or descending (desc).",
    default="asc",
)
@click.option("--after", "-a", help="ISO datetime to import customers after (FROM)")
@click.option("--before", "-b", help="ISO datetime to import customers before (TO)")
@click.option(
    "--days",
    "-d",
    type=click.INT,
    help="Import customers created in the past X days (default=0 today)",
    default=0,
)
@click.option(
    "--hours",
    "-h",
    type=click.INT,
    help="Import customers created in the past X hours (default=1 hour)",
    default=1,
)
def import_customers(id, sort, after, before, days, hours):
    """
    Import all customers created between a datetime range or specific customer
    """
    if id:
        print(f"Importing specific customer with ID {id}...\n")
        customers.get_customer(id)
        return

    if sort:
        if sort.startswith("asc"):
            sort = "asc"
        elif sort.startswith("desc"):
            sort = "desc"
        else:
            sort = "asc"

    if after and before:
        print(
            f"Importing all customers created after '{after}' and before '{before}' sorted '{sort}'...\n"
        )
        customers.import_all_customers(sort, after, before)
    else:
        current_time = datetime.datetime.now()
        today = datetime.date.today()
        if days > 0:
            # user has provided days argument
            start_day = today - datetime.timedelta(days=days)
        else:
            # default is today
            start_day = today

        if start_day != today:
            after = f"{str(start_day)}T{current_time}.000"
        else:
            if hours > 1:
                # hours argument provided
                start_time = current_time - datetime.timedelta(seconds=hours * 3600)
            else:
                # last 1 hour
                start_time = current_time - datetime.timedelta(seconds=3600)

            after = f'{start_time.strftime("%Y-%m-%dT%H:%M:%S")}.000'

        before = f'{current_time.strftime("%Y-%m-%dT%H:%M:%S")}.000'
        print(
            f"Importing all customers created after '{after}' and before '{before}' sorted '{sort}'...\n"
        )
        customers.import_all_customers(sort, after, before)


cli.add_command(import_orders)
cli.add_command(import_customers)


if __name__ == "__main__":
    cli()
