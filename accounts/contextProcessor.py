from vendor.models import Vendor
from food.settings import GOOGLE_API_KEY
def get_vednor(request):
    try:
        vendor = Vendor.objects.get(user=request.user)
    except:
        vendor=None
    return dict(vendor=vendor)

def get_google_api(request):
    return {'GOOGLE_API_KEY': GOOGLE_API_KEY}
