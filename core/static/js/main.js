/*price range*/

 $('#sl2').slider();

	var RGBChange = function() {
	  $('#RGB').css('background', 'rgb('+r.getValue()+','+g.getValue()+','+b.getValue()+')')
	};	
		
/*scroll to top*/

$(document).ready(function(){
	$(function () {
		$.scrollUp({
	        scrollName: 'scrollUp', // Element ID
	        scrollDistance: 300, // Distance from top/bottom before showing element (px)
	        scrollFrom: 'top', // 'top' or 'bottom'
	        scrollSpeed: 300, // Speed back to top (ms)
	        easingType: 'linear', // Scroll to top easing (see http://easings.net/)
	        animation: 'fade', // Fade, slide, none
	        animationSpeed: 200, // Animation in speed (ms)
	        scrollTrigger: false, // Set a custom triggering element. Can be an HTML string or jQuery object
					//scrollTarget: false, // Set a custom target element for scrolling to the top
	        scrollText: '<i class="fa fa-angle-up"></i>', // Text for element, can contain HTML
	        scrollTitle: false, // Set a custom <a> title if required.
	        scrollImg: false, // Set true to use image
	        activeOverlay: false, // Set CSS color to display scrollUp active point, e.g '#00FFFF'
	        zIndex: 2147483647 // Z-Index for the overlay
		});
	});
});



// filter
        // Initialize price range slider
document.addEventListener('DOMContentLoaded', function() {
    const priceSlider = document.getElementById('priceSlider');
    const minPriceInput = document.getElementById('minPrice');
    const maxPriceInput = document.getElementById('maxPrice');
    
    noUiSlider.create(priceSlider, {
        start: [0, 600],
        connect: true,
        range: {
            'min': 0,
            'max': 600
        },
        step: 10,
        tooltips: [true, true],
        format: {
            to: function(value) {
                return '$' + Math.round(value);
            },
            from: function(value) {
                return Number(value.replace('$', ''));
            }
        }
    });
    
    priceSlider.noUiSlider.on('update', function(values, handle) {
        const value = values[handle];
        if (handle) {
            maxPriceInput.value = value.replace('$', '');
        } else {
            minPriceInput.value = value.replace('$', '');
        }
    });
    
    minPriceInput.addEventListener('change', function() {
        priceSlider.noUiSlider.set([this.value, null]);
    });
    
    maxPriceInput.addEventListener('change', function() {
        priceSlider.noUiSlider.set([null, this.value]);
    });
});