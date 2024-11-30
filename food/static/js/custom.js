let autocompleteAddress, autocompleteLocation;

function initAutoComplete() {
    // Initialize autocomplete for Location field with auto-submit enabled
    autocompleteLocation = initAutocompleteForField('id_location', onPlaceChangedLocation, true);

    // Initialize autocomplete for Address field with auto-submit disabled
    autocompleteAddress = initAutocompleteForField('id_address', onPlaceChangedAddress, false);

    // Prevent default form submission on Enter for address and location fields
    preventEnterSubmission('id_address');
    preventEnterSubmission('id_location');
}

function initAutocompleteForField(fieldId, onChangeCallback, autoSubmit = false) {
    const inputField = document.getElementById(fieldId);
    const autocomplete = new google.maps.places.Autocomplete(
        inputField,
        { types: ['geocode', 'establishment'], componentRestrictions: { country: ['in'] } }
    );

    // Add listener for place_changed event
    autocomplete.addListener('place_changed', () => {
        onChangeCallback(autocomplete);

        // For location field, auto-submit form only after lat/long are updated
        if (autoSubmit) {
            setTimeout(() => {
                inputField.form.submit();
            }, 100); // Slight delay ensures lat/long are updated
        }
    });

    return autocomplete;
}

function preventEnterSubmission(fieldId) {
    const inputField = document.getElementById(fieldId);
    inputField.addEventListener('keydown', function (event) {
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default form submission
            // Trigger place_changed if Enter is pressed
            const autocompleteInstance = fieldId === 'id_location' ? autocompleteLocation : autocompleteAddress;
            google.maps.event.trigger(autocompleteInstance, 'place_changed');
        }
    });
}

function onPlaceChangedLocation(autocomplete) {
    updateLatLong(autocomplete, {
        latitudeField: 'id_latitude1',
        longitudeField: 'id_longitude1'
    });
}

function onPlaceChangedAddress(autocomplete) {
    updateLatLong(autocomplete, {
        latitudeField: 'id_latitude',
        longitudeField: 'id_longitude',
        extraFields: {
            country: 'id_country',
            state: 'id_state',
            city: 'id_city',
            pincode: 'id_pincode'
        }
    });
}

function updateLatLong(autocomplete, { latitudeField, longitudeField, extraFields = {} }) {
    const place = autocomplete.getPlace();
    if (!place.geometry) {
        console.warn("Place geometry not found");
        return;
    }

    // Update lat and lng
    const lat = place.geometry.location.lat();
    const lng = place.geometry.location.lng();
    setField(latitudeField, lat);
    setField(longitudeField, lng);

    // Update additional fields
    if (extraFields) {
        const addressComponents = place.address_components;
        for (const component of addressComponents) {
            const types = component.types;
            if (types.includes('country')) {
                setField(extraFields.country, component.long_name);
            } else if (types.includes('administrative_area_level_1')) {
                setField(extraFields.state, component.long_name);
            } else if (types.includes('administrative_area_level_3')) {
                setField(extraFields.city, component.long_name);
            } else if (types.includes('postal_code')) {
                setField(extraFields.pincode, component.long_name);
            }
        }
    }
}

function setField(fieldId, value) {
    if (fieldId && document.getElementById(fieldId)) {
        document.getElementById(fieldId).value = value || '';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Toggle the dropdown menu when the trigger is clicked
    const dropdownTrigger = document.querySelector('.dropdown > a');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    dropdownTrigger.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent default link behavior
        event.stopPropagation(); // Prevent event bubbling
        dropdownMenu.style.display = (dropdownMenu.style.display === 'block') ? 'none' : 'block';
    });

    // Close the dropdown menu when clicking outside of it
    document.addEventListener('click', function (event) {
        if (!event.target.closest('.dropdown')) {
            dropdownMenu.style.display = 'none';
        }
    });
});

 
$(document).ready(function(){
    //add to cart
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login'
                    })
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);  
                    
                    //subtotal, tax, total
                    getCartAmoounts(
                        response.get_cart_total['subtotal'],
                        response.get_cart_total['taxtotal'],
                        response.get_cart_total['total'],
                        response.get_cart_total['taxes'],
                    )
                }
            }
        })
    })

    //place the cart item quantity on load
    $('.item_qty').each(function(){
        var the_id = $(this).attr('id')
        var qty = $(this).attr('data-qty')
        $('#'+the_id).html(qty)
    })
     //decrease to cart
     $('.decrease_cart').on('click', function(e){
        e.preventDefault();
        
        food_id = $(this).attr('data-id');
        url = $(this).attr('data-url');
        cart_id = $(this).attr('item-id');
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if (response.status == 'login_required') {
                    swal(response.message, '', 'info').then(function(){
                        window.location = '/login'
                    })
                }else if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);    

                    if (window.location.pathname == '/cart/') {
                        removeCartItem(response.qty, cart_id);
                        chehckEmptyCart();   
                    }
                    //subtotal, tax, total
                    getCartAmoounts(
                        response.get_cart_total['subtotal'],
                        response.get_cart_total['taxtotal'],
                        response.get_cart_total['total'],
                        response.get_cart_total['taxes'],
                    )
                }
            }
        })
    })

    $('.delete_cart').on('click', function(e){
        e.preventDefault();

        cart_id = $(this).attr('data-id');
        url = $(this).attr('data-url');

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status == 'Failed'){
                    swal(response.message, '', 'error')
                }else {
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status, response.message, "success")
                    window.location.href = '/cart/';
                }
            }
        })
    })  

    function removeCartItem(cartItemQty, cart_id){
        if(cartItemQty <= 0){
            document.getElementById("cart-item-"+cart_id).remove()
        }
    }

    function chehckEmptyCart(){
        var cart_counter = document.getElementById('cart_counter').innerHTML
        if (cart_counter == 0) {
            document.getElementById("empty-cart").style.display = "block";
        }
    }


    function getCartAmoounts(subtotal, taxtotal, total, taxes) {
        if (window.location.pathname == '/cart/') {
            // Update subtotal and total
            $('.subtotal').html(subtotal);
            $('#total').html(total);
            $('#taxtotal').html(taxtotal);
    
            // Update each tax type individually
            $.each(taxes, function(taxtype, taxes) {
                var taxPercentage = taxes[0]; // This is the tax percentage
                var taxAmount = taxes[1];     // This is the tax amount
    
                // Update the tax amount in the DOM based on the tax type
                $('#tax-' + taxtype).html(taxAmount);
            });
        }
    }

    $('.add_hour').on('click', function(e) {
        e.preventDefault();
        var day = document.getElementById('id_day').value;
        var from_hour = document.getElementById('id_from_hour').value;
        var to_hour = document.getElementById('id_to_hour').value;
        var is_closed = document.getElementById('id_is_closed').checked;
        var csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        var url = document.getElementById('add_hour_url').value;
    
        // Condition to validate the form input
        var condition = "(is_closed && from_hour == '' && to_hour == '') || (!is_closed && from_hour != '' && to_hour != '')";
        if (day != '') {
            if (eval(condition)) {
                $.ajax({
                    type: 'POST',
                    url: url,
                    data: {
                        'day': day,
                        'from_hour': from_hour,
                        'to_hour': to_hour,
                        'is_closed': is_closed,
                        'csrfmiddlewaretoken': csrf_token,
                    },
                    success: function(response) {
                        if (response.status == 'success') {
                            var existingRow = $(`#hour-${response.id}`);
                            var html;
    
                            if (response.is_closed == 'Closed') {
                                html = `Closed`;
                            } else {
                                html = `${response.from_hour} - ${response.to_hour}`;
                            }
    
                            // Update the existing row
                            existingRow.find('td:nth-child(2)').html(html);
    
                            document.getElementById('opening_hours').reset();
                            swal(response.message, '', 'success');
                        } else {
                            swal(response.message, '', 'error');
                            console.log(response.message)
                        }
                    }
                });
            } else {
                swal('Select hours or closed. You cannot select both. Fill both "from" and "to" hour fields if you are filling hours.', '', 'error');
            }
        } else {
            swal("Please fill the required fields", '', 'error');
        }
    });
    

});
