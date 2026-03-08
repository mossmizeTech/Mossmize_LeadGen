"""
Celery Task Pipeline
Defines all pipeline stages as Celery tasks connected in the correct order.
"""

import asyncio
import logging
from datetime import datetime, timezone

from bson import ObjectId

from app.celery_app import celery_app
from app.config import settings

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from within a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def _get_sync_db():
    """Get a synchronous pymongo database handle for Celery tasks."""
    from pymongo import MongoClient
    client = MongoClient(settings.mongo_uri)
    return client[settings.mongo_db_name]


@celery_app.task(bind=True, name="app.tasks.pipeline.task_generate_grids", max_retries=3)
def task_generate_grids(self, city: str, grid_size_km: float = None):
    """
    Stage 1: Generate grid coordinates for a city.
    Returns list of grid points.
    """
    from app.modules.grid_generator import generate_city_grid

    try:
        grid_points = _run_async(generate_city_grid(city, grid_size_km))
        logger.info("Generated %d grid points for city '%s'", len(grid_points), city)
        return {"city": city, "grid_points": grid_points, "count": len(grid_points)}
    except Exception as exc:
        logger.error("Grid generation failed for '%s': %s", city, exc)
        raise self.retry(exc=exc, countdown=10)


@celery_app.task(bind=True, name="app.tasks.pipeline.task_expand_keywords", max_retries=1)
def task_expand_keywords(self, keywords: list[str]):
    """
    Stage 2: Expand seed keywords into niche search terms.
    Returns expanded keyword list.
    """
    from app.modules.keyword_engine import expand_keywords

    expanded = expand_keywords(keywords)
    logger.info("Expanded %d keywords into %d terms", len(keywords), len(expanded))
    return {"keywords": expanded, "count": len(expanded)}


@celery_app.task(bind=True, name="app.tasks.pipeline.task_search_maps", max_retries=3)
def task_search_maps(self, keyword: str, lat: float, lng: float, city: str):
    """
    Stage 3: Search Google Maps for businesses at a grid point.
    Stores discovered businesses in MongoDB.
    Returns list of place_ids.
    """
    from app.modules.maps_search import search_nearby

    try:
        businesses = _run_async(search_nearby(keyword, lat, lng))
    except Exception as exc:
        logger.error("Maps search failed for '%s' at (%s,%s): %s", keyword, lat, lng, exc)
        raise self.retry(exc=exc, countdown=15)

    db = _get_sync_db()
    place_ids = []

    for biz in businesses:
        biz["city"] = city
        biz["category"] = keyword
        biz["scraped_at"] = datetime.now(timezone.utc)

        # Upsert by place_id
        db.businesses.update_one(
            {"place_id": biz["place_id"]},
            {"$set": biz},
            upsert=True,
        )
        place_ids.append(biz["place_id"])

    logger.info("Stored %d businesses for '%s' at (%s,%s)", len(place_ids), keyword, lat, lng)
    return {"place_ids": place_ids, "count": len(place_ids)}


@celery_app.task(bind=True, name="app.tasks.pipeline.task_fetch_details", max_retries=3)
def task_fetch_details(self, place_id: str):
    """
    Stage 4: Fetch detailed info for a business from Place Details API.
    Updates the business record in MongoDB.
    """
    from app.modules.place_details import fetch_details

    try:
        details = _run_async(fetch_details(place_id))
    except Exception as exc:
        logger.error("Place details failed for %s: %s", place_id, exc)
        raise self.retry(exc=exc, countdown=15)

    if not details:
        return {"place_id": place_id, "website": None}

    db = _get_sync_db()
    update_fields = {}
    if details.get("website"):
        update_fields["website"] = details["website"]
    if details.get("phone_number"):
        update_fields["phone"] = details["phone_number"]
    if details.get("google_maps_url"):
        update_fields["google_maps_url"] = details["google_maps_url"]
    if details.get("opening_hours"):
        update_fields["opening_hours"] = details["opening_hours"]
    if details.get("formatted_address"):
        update_fields["address"] = details["formatted_address"]

    if update_fields:
        db.businesses.update_one({"place_id": place_id}, {"$set": update_fields})

    return {"place_id": place_id, "website": details.get("website")}


@celery_app.task(bind=True, name="app.tasks.pipeline.task_discover_website", max_retries=2)
def task_discover_website(self, place_id: str, business_name: str, city: str):
    """
    Stage 4b: Fallback website discovery when Places API has no website.
    """
    from app.modules.website_discovery import discover_website

    try:
        website = _run_async(discover_website(business_name, city))
    except Exception as exc:
        logger.error("Website discovery failed for '%s': %s", business_name, exc)
        raise self.retry(exc=exc, countdown=10)

    if website:
        db = _get_sync_db()
        db.businesses.update_one(
            {"place_id": place_id},
            {"$set": {"website": website}},
        )

    return {"place_id": place_id, "website": website}


@celery_app.task(bind=True, name="app.tasks.pipeline.task_crawl_website", max_retries=2)
def task_crawl_website(self, place_id: str, website_url: str):
    """
    Stage 5: Crawl a business website and extract emails.
    Stores validated emails in MongoDB.
    """
    from app.modules.website_crawler import crawl_website
    from app.modules.email_extractor import extract_emails_from_pages
    from app.modules.email_pattern import generate_pattern_emails
    from app.modules.email_validator import validate_emails

    try:
        # Crawl the website
        pages = _run_async(crawl_website(website_url))
    except Exception as exc:
        logger.error("Crawl failed for %s: %s", website_url, exc)
        raise self.retry(exc=exc, countdown=20)

    # Extract emails from crawled pages
    extracted = extract_emails_from_pages(pages)
    email_list = [e["email"] for e in extracted]
    source_map = {e["email"]: e.get("source_page", "") for e in extracted}

    # If no emails found, generate pattern emails
    if not email_list:
        pattern_emails = generate_pattern_emails(website_url)
        email_list.extend(pattern_emails)
        for pe in pattern_emails:
            source_map[pe] = "pattern_generated"

    if not email_list:
        return {"place_id": place_id, "emails_found": 0}

    # Validate emails
    valid_results = _run_async(validate_emails(email_list))

    # Store in MongoDB
    db = _get_sync_db()
    business = db.businesses.find_one({"place_id": place_id})
    business_id = str(business["_id"]) if business else place_id

    stored_count = 0
    for vr in valid_results:
        email_doc = {
            "business_id": business_id,
            "email": vr["email"],
            "source_page": source_map.get(vr["email"], ""),
            "validated": True,
            "validation_method": vr.get("method", "mx"),
            "created_at": datetime.now(timezone.utc),
        }
        try:
            db.emails.update_one(
                {"email": vr["email"], "business_id": business_id},
                {"$set": email_doc},
                upsert=True,
            )
            stored_count += 1
        except Exception as e:
            logger.warning("Failed to store email %s: %s", vr["email"], e)

    logger.info("Stored %d validated emails for place_id=%s", stored_count, place_id)
    return {"place_id": place_id, "emails_found": stored_count}


@celery_app.task(name="app.tasks.pipeline.task_orchestrate_search")
def task_orchestrate_search(city: str, keywords: list[str]):
    """
    Master orchestrator: kicks off the full pipeline for a city + keywords.
    1. Generate grids
    2. Expand keywords
    3. For each keyword × grid point → search maps
    4. For each business → fetch details
    5. For each business with website → crawl + extract emails
    """
    from celery import chain, group, chord

    # Step 1: Generate grids
    grid_result = task_generate_grids.apply(args=[city])
    grid_data = grid_result.get(timeout=120)
    grid_points = grid_data["grid_points"]

    # Step 2: Expand keywords
    kw_result = task_expand_keywords.apply(args=[keywords])
    kw_data = kw_result.get(timeout=30)
    expanded_keywords = kw_data["keywords"]

    # Step 3: Search maps — dispatch all keyword × grid combinations
    search_tasks = []
    for kw in expanded_keywords:
        for point in grid_points:
            search_tasks.append(
                task_search_maps.s(kw, point["lat"], point["lng"], city)
            )

    # Execute search tasks in batches
    batch_size = 50
    all_place_ids = set()

    for i in range(0, len(search_tasks), batch_size):
        batch = group(search_tasks[i:i + batch_size])
        results = batch.apply_async()
        for result in results.get(timeout=600):
            if isinstance(result, dict) and "place_ids" in result:
                all_place_ids.update(result["place_ids"])

    logger.info("Total unique businesses found: %d", len(all_place_ids))
    return {
        "city": city,
        "total_businesses": len(all_place_ids),
        "place_ids": list(all_place_ids),
    }


@celery_app.task(name="app.tasks.pipeline.task_orchestrate_scraping")
def task_orchestrate_scraping(city: str = None, limit: int = 1000):
    """
    Master orchestrator for the scraping pipeline:
    1. Fetch details for businesses without website info
    2. Discover websites for businesses without websites
    3. Crawl websites and extract emails
    """
    from celery import group

    db = _get_sync_db()

    # Find businesses to process
    query = {}
    if city:
        query["city"] = city

    businesses = list(db.businesses.find(query).limit(limit))

    # Step 1: Fetch details for businesses missing website
    detail_tasks = []
    for biz in businesses:
        if not biz.get("website") and not biz.get("phone"):
            detail_tasks.append(task_fetch_details.s(biz["place_id"]))

    if detail_tasks:
        batch_size = 50
        for i in range(0, len(detail_tasks), batch_size):
            batch = group(detail_tasks[i:i + batch_size])
            batch.apply_async().get(timeout=600)

    # Refresh business data
    businesses = list(db.businesses.find(query).limit(limit))

    # Step 2: Discover websites for those still missing
    discovery_tasks = []
    for biz in businesses:
        if not biz.get("website"):
            discovery_tasks.append(
                task_discover_website.s(
                    biz["place_id"],
                    biz["business_name"],
                    biz.get("city", ""),
                )
            )

    if discovery_tasks:
        batch_size = 20
        for i in range(0, len(discovery_tasks), batch_size):
            batch = group(discovery_tasks[i:i + batch_size])
            batch.apply_async().get(timeout=600)

    # Refresh again
    businesses = list(db.businesses.find(query).limit(limit))

    # Step 3: Crawl websites and extract emails
    crawl_tasks = []
    for biz in businesses:
        if biz.get("website"):
            # Check if we already have emails for this business
            existing_emails = db.emails.count_documents({"business_id": str(biz["_id"])})
            if existing_emails == 0:
                crawl_tasks.append(
                    task_crawl_website.s(biz["place_id"], biz["website"])
                )

    total_emails = 0
    if crawl_tasks:
        batch_size = 10
        for i in range(0, len(crawl_tasks), batch_size):
            batch = group(crawl_tasks[i:i + batch_size])
            results = batch.apply_async().get(timeout=1200)
            for r in results:
                if isinstance(r, dict):
                    total_emails += r.get("emails_found", 0)

    logger.info("Scraping complete: %d emails extracted", total_emails)
    return {
        "city": city,
        "businesses_processed": len(businesses),
        "emails_extracted": total_emails,
    }
