from typing import List, Dict, Any
from metadata_analysis.models import Asset, Event, StockImpact

def get_metadata_for_stock(stock_name: str) -> List[Dict[str, Any]]:
    """
    Retrieve existing events and stock impact data for assets belonging to the given stock/company name.
    Returns a list of dicts with event and impact details.
    """
    # Query assets by company name or ticker symbol (case insensitive)
    assets = Asset.objects.filter(company__name__iexact=stock_name) | Asset.objects.filter(company__ticker_symbol__iexact=stock_name)
    assets = assets.distinct()  # remove duplicates if any

    if not assets.exists():
        print(f"No assets found for stock/company: {stock_name}")
        return []

    results = []

    for asset in assets:
        # Get events linked to this asset via many-to-many 'matched_assets'
        events = Event.objects.filter(matched_assets=asset)

        for event in events:
            # Try to get the stock impact related to this company and event
            try:
                stock_impact = StockImpact.objects.get(company=asset.company, event=event)
                impact = stock_impact.predicted_impact or "Unknown"
                confidence = stock_impact.confidence_score
            except StockImpact.DoesNotExist:
                impact = "Unknown"
                confidence = None

            results.append({
                "company": asset.company.name,
                "asset_name": asset.name,
                "event_title": event.title,
                "event_date": event.date.strftime('%Y-%m-%d') if event.date else None,
                "event_type": event.event_type,
                "event_location": event.location,
                "event_sentiment": event.sentiment,
                "stock_impact": impact,
                "confidence_score": confidence,
                "event_summary": event.summary,
            })

    print("Metadata results:")
    # print(results)

    return results
