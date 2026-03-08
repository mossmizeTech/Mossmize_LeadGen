"""
FastAPI Admin API Routes
Endpoints for starting searches, scraping, viewing leads, stats, and export.
"""

import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel

from app.database import get_db
from app.tasks.pipeline import (
    task_orchestrate_search,
    task_orchestrate_scraping,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# ---------- Request/Response Models ----------

class SearchRequest(BaseModel):
    """Request body for starting a search."""
    city: str
    keywords: list[str]
    grid_size_km: Optional[float] = None


class ScrapeRequest(BaseModel):
    """Request body for starting the scraping pipeline."""
    city: Optional[str] = None
    limit: int = 1000


class SearchResponse(BaseModel):
    task_id: str
    message: str
    city: str
    keywords: list[str]


class ScrapeResponse(BaseModel):
    task_id: str
    message: str


# ---------- Endpoints ----------

@router.post("/start-search", response_model=SearchResponse)
async def start_search(req: SearchRequest):
    """
    Start a new Google Maps search job.
    Generates grid, expands keywords, searches all grid×keyword combinations.
    """
    if not req.city.strip():
        raise HTTPException(status_code=400, detail="City is required")
    if not req.keywords:
        raise HTTPException(status_code=400, detail="At least one keyword is required")

    task = task_orchestrate_search.delay(req.city.strip(), req.keywords)

    return SearchResponse(
        task_id=task.id,
        message=f"Search started for '{req.city}' with {len(req.keywords)} keywords",
        city=req.city,
        keywords=req.keywords,
    )


@router.post("/start-scraping", response_model=ScrapeResponse)
async def start_scraping(req: ScrapeRequest):
    """
    Start the scraping pipeline (details → website discovery → crawl → email extraction).
    """
    task = task_orchestrate_scraping.delay(city=req.city, limit=req.limit)

    return ScrapeResponse(
        task_id=task.id,
        message=f"Scraping pipeline started" + (f" for city '{req.city}'" if req.city else ""),
    )


@router.get("/leads")
async def get_leads(
    city: Optional[str] = Query(None, description="Filter by city"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=500, description="Items per page"),
    has_email: Optional[bool] = Query(None, description="Filter businesses with/without emails"),
):
    """
    Get paginated list of leads (businesses with their emails).
    """
    db = get_db()
    skip = (page - 1) * page_size

    # Build query
    query = {}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}

    # Get businesses
    cursor = db.businesses.find(query).skip(skip).limit(page_size).sort("scraped_at", -1)
    businesses = await cursor.to_list(length=page_size)

    # Get total count
    total = await db.businesses.count_documents(query)

    # Enrich with emails
    leads = []
    for biz in businesses:
        biz_id = str(biz["_id"])
        emails_cursor = db.emails.find({"business_id": biz_id})
        emails = await emails_cursor.to_list(length=100)

        lead = {
            "business_name": biz.get("business_name", ""),
            "place_id": biz.get("place_id", ""),
            "address": biz.get("address", ""),
            "website": biz.get("website"),
            "phone": biz.get("phone"),
            "city": biz.get("city", ""),
            "category": biz.get("category"),
            "rating": biz.get("rating"),
            "latitude": biz.get("latitude"),
            "longitude": biz.get("longitude"),
            "emails": [e.get("email", "") for e in emails],
            "scraped_at": biz.get("scraped_at"),
        }

        if has_email is True and not lead["emails"]:
            continue
        if has_email is False and lead["emails"]:
            continue

        leads.append(lead)

    return {
        "leads": leads,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


@router.get("/stats")
async def get_stats():
    """
    Get summary statistics of the lead database.
    """
    db = get_db()

    total_businesses = await db.businesses.count_documents({})
    total_emails = await db.emails.count_documents({})
    validated_emails = await db.emails.count_documents({"validated": True})

    # Businesses with websites
    with_website = await db.businesses.count_documents({"website": {"$ne": None, "$exists": True}})

    # Stats per city
    pipeline = [
        {"$group": {
            "_id": "$city",
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    city_stats_cursor = db.businesses.aggregate(pipeline)
    city_stats = await city_stats_cursor.to_list(length=20)

    return {
        "total_businesses": total_businesses,
        "businesses_with_website": with_website,
        "total_emails": total_emails,
        "validated_emails": validated_emails,
        "website_coverage": f"{(with_website / total_businesses * 100):.1f}%" if total_businesses > 0 else "0%",
        "email_rate": f"{(total_emails / total_businesses * 100):.1f}%" if total_businesses > 0 else "0%",
        "by_city": [
            {"city": s["_id"] or "Unknown", "businesses": s["count"]}
            for s in city_stats
        ],
    }


@router.get("/export")
async def export_leads(
    format: str = Query("csv", description="Export format: csv or json"),
    city: Optional[str] = Query(None, description="Filter by city"),
):
    """
    Export leads as CSV or JSON.
    """
    db = get_db()

    query = {}
    if city:
        query["city"] = {"$regex": city, "$options": "i"}

    cursor = db.businesses.find(query).sort("scraped_at", -1)
    businesses = await cursor.to_list(length=100000)

    # Build export data
    rows = []
    for biz in businesses:
        biz_id = str(biz["_id"])
        emails_cursor = db.emails.find({"business_id": biz_id})
        emails = await emails_cursor.to_list(length=100)
        email_list = [e.get("email", "") for e in emails]

        rows.append({
            "business_name": biz.get("business_name", ""),
            "email": "; ".join(email_list),
            "website": biz.get("website", ""),
            "phone": biz.get("phone", ""),
            "city": biz.get("city", ""),
            "address": biz.get("address", ""),
            "category": biz.get("category", ""),
            "rating": biz.get("rating", ""),
        })

    if format.lower() == "json":
        return JSONResponse(content={"leads": rows, "total": len(rows)})

    # CSV export
    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    else:
        output.write("business_name,email,website,phone,city,address,category,rating\n")

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"leads_export_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
