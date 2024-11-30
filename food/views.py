from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from vendor.models import Vendor

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from django.db.models import Q
def home(request):
        
    location = request.session.get('location', '')
    lat = request.session.get('lat', '')
    long = request.session.get('long', '')
    print("hello")
    print(location, lat, long)

    if request.GET:
        location = request.GET.get('location')
        lat = request.GET.get('lat')
        long = request.GET.get('long')

        request.session['location'] = location
        request.session['lat'] = lat
        request.session['long'] = long

    print("hello again")
    print(location, lat, long)
    
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    if long and lat:
        pnt = GEOSGeometry(f"POINT({long} {lat})")
        vendors = vendors.filter(
            vendor_profile__location__distance_lte=(pnt, D(km=75))
        ).annotate(
        distance=Distance('vendor_profile__location', pnt)
    ).order_by('distance')[:6]
        
    

    context = {
        "vendors":vendors,
        'location': location,
        'lat': lat,
        'long': long,
    }
    return render(request, 'home.html', context)
