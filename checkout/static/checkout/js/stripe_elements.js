/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

var stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
var clientSecret = $('#id_client_secret').text().slice(1, -1);
var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();
var style = {
    base: {
        color: '#000',
        // fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        // fontSmoothing: 'antialiased',
        // fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
var card = elements.create('card', {style: style});
card.mount('#card-element');

// Fix for Stripe Elements aria-hidden accessibility warning
// Use MutationObserver to continuously remove aria-hidden from Stripe card element
var cardElementContainer = document.getElementById('card-element');
if (cardElementContainer) {
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'aria-hidden') {
                cardElementContainer.removeAttribute('aria-hidden');
                // Also remove from any nested iframes or elements
                var iframes = cardElementContainer.querySelectorAll('iframe');
                iframes.forEach(function(iframe) {
                    iframe.removeAttribute('aria-hidden');
                });
            }
        });
    });
    
    var config = {
        attributes: true,
        attributeFilter: ['aria-hidden'],
        subtree: true
    };
    observer.observe(cardElementContainer, config);
}

// Handle realtime validation errors on the card element
card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    if (event.error) {
        var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times" aria-hidden="true"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
var form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    $('#form-instructions').fadeToggle(100);
    $('#payment-form').fadeToggle(100);
    $('#processing-message').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    var saveInfo = Boolean($('#id-save-info').attr('checked'));
    // From using {% csrf_token %} in the form
    var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
        'email': $.trim(form.email.value),
    };
    var url = '/checkout/cache_checkout_data/';

    $.post(url, postData).done(function () {
        var fullName = $.trim($('#id_first_name').val()) + ' ' + $.trim($('#id_last_name').val());
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: fullName,
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: 'GB', // Always UK for delivery
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: fullName,
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: 'GB', // Always UK for delivery
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                var errorDiv = document.getElementById('card-errors');
                var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times" aria-hidden="true"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                $('#form-instructions').fadeToggle(100);
                $('#payment-form').fadeToggle(100);
                $('#processing-message').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
    })
});