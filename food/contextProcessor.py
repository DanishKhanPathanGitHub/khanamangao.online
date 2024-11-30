def location_data(request):
    location = request.session.get('location', '')
    lat = request.session.get('lat', '')
    long = request.session.get('long', '')

    return {
        'location':location,
        'lat':lat,
        'long':long,
    }