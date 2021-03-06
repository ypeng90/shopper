from product.data import ProductMySQLInterface
from product.utils import Downloader
from celery import shared_task, chain
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import json
from time import sleep

logger = get_task_logger(__name__)


@shared_task(
    # bound to self instance
    bind=True,
    # in-queue expiry time: in 1 hour
    utc=True,
    expires=datetime.utcnow() + timedelta(hours=1),
    # (soft, hard) execution time limits
    # SoftTimeLimitExceeded exception is raised when
    # soft time limit is reached.
    timelimit=(25, 30),
    # retry with max_retries and backoff
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    # select queue
    queue="slow",
)
def get_quantity_from_store(self, count, sku, store, zipcode):
    logger.info(f"Get quantity for {sku} at {store} around {zipcode}")
    sleep(0.5)
    info = []
    # variation exists, not always 20
    if store == "tgt" and count < 18:
        downloader = Downloader(
            "http://scraper-web:8000/scraper/"
            f"target/quantity/{sku}/{zipcode}/"
        )
        resp = downloader.response
        if resp and resp.status_code == 200:
            try:
                info = resp.json().get("info")
            except Exception:
                logger.exception(f"get_quantity_from_store : {sku}-{zipcode}")
            if info is None:
                info = []
    return info


@shared_task(
    # in-queue expiry time: in 1 hour
    utc=True,
    expires=datetime.utcnow() + timedelta(hours=1),
    # (soft, hard) execution time limits
    # SoftTimeLimitExceeded exception is raised when
    # soft time limit is reached.
    timelimit=(25, 30),
    # acknowledge after execution for idempotent
    # procedures
    acks_late=True,
    # select queue
    queue="celery",
)
def add_quantity_to_db(info):
    if info:
        ProductMySQLInterface.add_quantity(info)


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
)
def count_quantity(sku, store, zipcode):
    # count of stores with the latest quantity
    count = 0
    data = ProductMySQLInterface.count_store_with_latest(sku, store, zipcode)
    if data:
        count = data[0][0]
    return count


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
    queue="fast",
)
def count_get_add_quantity(sku, store, zipcode):
    chain(
        count_quantity.s(sku, store, zipcode),
        get_quantity_from_store.s(sku, store, zipcode),
        add_quantity_to_db.s()
    ).delay()


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
)
def get_tracked_products(userid):
    zipcode = ""
    products = []
    data = ProductMySQLInterface.get_zipcode(userid)
    if data:
        zipcode = data[0][0]
    if zipcode:
        data = ProductMySQLInterface.list_all_track_products(userid)
        if data:
            products = json.loads(data[0][0])
    return zipcode, products


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
)
def get_quantity_per_product(zipcode_products):
    zipcode, products = zipcode_products
    for product in products:
        sku = product["sku"]
        store = product["store"]
        count_get_add_quantity.delay(sku, store, zipcode)


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
    queue="fast",
)
def preload(userid):
    chain(
        get_tracked_products.s(userid),
        get_quantity_per_product.s()
    ).delay()


@shared_task(
    utc=True,
    expires=datetime.utcnow() + timedelta(minutes=5),
    timelimit=(25, 30),
    acks_late=True,
)
def update_zipcode(userid, zipcode):
    ProductMySQLInterface.update_zipcode(userid, zipcode)
