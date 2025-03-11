import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

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

        if response.status_code == 200:
            try:
                tracking_data = response.json()
            except ValueError:
                tracking_data = {"error": "Invalid response format (not JSON).", "response_text": response.text}
        else:
            tracking_data = {"error": f"Failed to fetch tracking data. Status Code: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        tracking_data = {"error": "Network error. Please try again later.", "details": str(e)}

    return render(request, "tracking/tracking.html", {"tracking_info": tracking_data})
