/* ===================================================
   CUSTOMIZE.JS — Curtain Customization Builder
   =================================================== */

document.addEventListener('DOMContentLoaded', function () {

    const form = document.getElementById('customization-form');
    if (!form) return;

    /* ---------- Element References ---------- */
    const widthInput = form.querySelector('[name="width"]');
    const heightInput = form.querySelector('[name="height"]');
    const fabricTypeSelect = form.querySelector('[name="fabric_type"]');
    const fabricColorSelect = form.querySelector('[name="fabric_color"]');
    const styleSelect = form.querySelector('[name="style"]');
    const headingSelect = form.querySelector('[name="heading_type"]');
    const innerCurtainCheck = form.querySelector('[name="include_inner_curtain"]');
    const innerFabricSelect = form.querySelector('[name="inner_fabric"]');
    const quantityInput = form.querySelector('[name="quantity"]');
    const priceDisplay = document.getElementById('live-price');
    const priceContainer = document.getElementById('price-container');
    const innerOptions = document.getElementById('inner-curtain-options');

    /* ---------- CSRF Token ---------- */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrfToken = getCookie('csrftoken');

    /* ---------- Inner Curtain Toggle ---------- */
    if (innerCurtainCheck && innerOptions) {
        const toggleInnerOptions = () => {
            if (innerCurtainCheck.checked) {
                innerOptions.classList.add('show');
                if (innerFabricSelect) innerFabricSelect.required = true;
            } else {
                innerOptions.classList.remove('show');
                if (innerFabricSelect) {
                    innerFabricSelect.required = false;
                    innerFabricSelect.value = '';
                }
            }
            calculatePrice();
        };

        innerCurtainCheck.addEventListener('change', toggleInnerOptions);
        // Initialize state
        toggleInnerOptions();
    }

    /* ---------- Color Swatch Selector ---------- */
    const swatches = document.querySelectorAll('.color-swatch');
    swatches.forEach(swatch => {
        swatch.addEventListener('click', function () {
            // Remove selected from all
            swatches.forEach(s => s.classList.remove('selected'));
            // Select this one
            this.classList.add('selected');
            // Update hidden select
            if (fabricColorSelect) {
                fabricColorSelect.value = this.dataset.colorId;
                calculatePrice();
            }
        });
    });

    /* ---------- Live Price Calculation ---------- */
    let priceTimeout;

    function calculatePrice() {
        clearTimeout(priceTimeout);

        priceTimeout = setTimeout(() => {
            const width = widthInput ? widthInput.value : '';
            const height = heightInput ? heightInput.value : '';
            const fabricType = fabricTypeSelect ? fabricTypeSelect.value : '';
            const fabricColor = fabricColorSelect ? fabricColorSelect.value : '';
            const style = styleSelect ? styleSelect.value : '';
            const headingType = headingSelect ? headingSelect.value : '';
            const includeInner = innerCurtainCheck ? innerCurtainCheck.checked : false;
            const innerFabric = innerFabricSelect ? innerFabricSelect.value : '';
            const quantity = quantityInput ? quantityInput.value : '1';

            // Validate required fields
            if (!width || !height || !fabricType || !fabricColor || !style || !headingType) {
                if (priceDisplay) {
                    priceDisplay.textContent = '—';
                }
                return;
            }

            // Show loading
            if (priceDisplay) {
                priceDisplay.innerHTML = '<span class="spinner-gold"></span>';
            }

            const formData = new FormData();
            formData.append('width', width);
            formData.append('height', height);
            formData.append('fabric_type', fabricType);
            formData.append('fabric_color', fabricColor);
            formData.append('style', style);
            formData.append('heading_type', headingType);
            formData.append('include_inner_curtain', includeInner.toString());
            formData.append('inner_fabric', innerFabric);
            formData.append('quantity', quantity);

            fetch('/calculate-price/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                if (data.price_display && priceDisplay) {
                    priceDisplay.textContent = data.price_display;
                    priceContainer?.classList.add('pulse');
                    setTimeout(() => priceContainer?.classList.remove('pulse'), 600);
                } else if (data.error && priceDisplay) {
                    priceDisplay.textContent = '—';
                }
            })
            .catch(err => {
                console.error('Price calculation error:', err);
                if (priceDisplay) {
                    priceDisplay.textContent = '—';
                }
            });
        }, 300); // Debounce 300ms
    }

    /* ---------- Attach Event Listeners ---------- */
    const priceInputs = [widthInput, heightInput, fabricTypeSelect, fabricColorSelect,
                         styleSelect, headingSelect, innerFabricSelect, quantityInput];
    
    priceInputs.forEach(input => {
        if (input) {
            input.addEventListener('change', calculatePrice);
            input.addEventListener('input', calculatePrice);
        }
    });

    /* ---------- Form Validation ---------- */
    if (form) {
        form.addEventListener('submit', function (e) {
            const width = parseFloat(widthInput?.value || 0);
            const height = parseFloat(heightInput?.value || 0);

            if (width < 12 || width > 240) {
                e.preventDefault();
                showValidationError(widthInput, 'Width must be between 12 and 240 inches');
                return;
            }

            if (height < 12 || height > 240) {
                e.preventDefault();
                showValidationError(heightInput, 'Height must be between 12 and 240 inches');
                return;
            }

            if (innerCurtainCheck?.checked && !innerFabricSelect?.value) {
                e.preventDefault();
                showValidationError(innerFabricSelect, 'Please select an inner curtain fabric');
                return;
            }
        });
    }

    function showValidationError(element, message) {
        if (!element) return;
        
        // Remove existing error
        const existing = element.parentNode.querySelector('.validation-error');
        if (existing) existing.remove();

        element.style.borderColor = '#C0392B';
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'validation-error';
        errorDiv.style.cssText = 'color: #C0392B; font-size: 0.8rem; margin-top: 0.25rem; font-weight: 500;';
        errorDiv.textContent = message;
        element.parentNode.appendChild(errorDiv);

        element.addEventListener('input', function handler() {
            element.style.borderColor = '';
            const err = element.parentNode.querySelector('.validation-error');
            if (err) err.remove();
            element.removeEventListener('input', handler);
        }, { once: true });

        element.focus();
    }

    // Initial price calculation if fields are pre-filled
    calculatePrice();
});
