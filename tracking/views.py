import requests
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the Tracking API!")

def track_view(request):
    tracking_number = request.GET.get("tracking_number")

    if not tracking_number:
        return render(request, "tracking/tracking.html", {"tracking_info": "Please enter a valid tracking number."})

    # Chronopost API URL
    chronopost_url = f"https://www.chronopost.fr/tracking-no-cms/suivi-colis?pod=true&listeNumerosLT={tracking_number}&langue=en"

    session = requests.Session()
    headers = {
        "Referer": "https://www.chronopost.fr/",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response = session.get(chronopost_url, headers=headers, timeout=10)

        if response.status_code != 200:
            return render(request, "tracking/tracking.html", {"tracking_info": f"Failed to fetch tracking data. Status Code: {response.status_code}"})

        try:
            tracking_data = response.json()
        except ValueError:
            return render(request, "tracking/tracking.html", {"tracking_info": "Invalid response format (not JSON)."})

        # Extract the tracking table HTML
        tracking_html = tracking_data.get("tab", "")

        # Parse HTML using BeautifulSoup
        soup = BeautifulSoup(tracking_html, "html.parser")

        # Find the tracking table
        table = soup.find("table", {"id": "suiviTab"})
        tracking_details = []

        # Extract table rows (skip the header row)
        if table:
            rows = table.find_all("tr", class_="toggleElmt")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    date_time = cols[0].get_text(strip=True)
                    location_status = cols[1].get_text(strip=True)
                    tracking_details.append({"date_time": date_time, "status": location_status})

        # If no tracking details found, show message
        if not tracking_details:
            tracking_details = [{"date_time": "N/A", "status": "No tracking information available"}]

        # Pass extracted tracking details to the template
        return render(request, "tracking/tracking.html", {"tracking_info": tracking_details})

    except requests.exceptions.RequestException as e:
        return render(request, "tracking/tracking.html", {"tracking_info": f"Network error. Please try again later. Details: {str(e)}"})
