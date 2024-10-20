function updateQuantityDirect(id,stock, name, desc, price, category, image) {
    console.log('int the cart');
    var quantity = parseInt(document.getElementById('quantity' + id).value);
    stock=parseInt(stock);
    if (quantity > 0) {
        if (quantity > stock) {
            alert("Sorry, we only have " + stock + " in stock of " + name);
            document.getElementById('quantity' + id).value=stock;
            quantity=stock
            cart['pr' + id] = [quantity, name, desc, price, category, image];
        }else{
            cart['pr' + id] = [quantity, name, desc, price, category, image];
        }
    } else {
        delete cart['pr' + id]
        document.getElementById('quantity-controls-' + id).style.display = 'none';
        document.getElementById('pr' + id).style.display = 'inline-block';
    }
    localStorage.setItem('cart', JSON.stringify(cart))
    var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
    document.getElementById('cartDisplay').innerHTML = total;
}
function deleteProduct(id) {
    var item = document.getElementById('cart-item-' + id);
    if (item) {
        item.innerHTML = "";
        item.style.display = 'none';
    }
    delete cart['pr' + id];
    console.log(cart);
    localStorage.setItem('cart', JSON.stringify(cart));
    submitForm();
}

function updateQuantity(id,stock,name, desc, price, category, image, delta) {
    var idstr = 'pr' + id;
    stock=parseInt(stock);
    var quantityInput = document.getElementById("quantity" + id);
    console.log("Update q");
    var newValue = parseInt(quantityInput.value) + delta;
    if (newValue > 0) {
        if (newValue > stock) {
            alert("Sorry, we only have " + stock + " in stock of " + name);
            document.getElementById('quantity' + id).value=stock;
            quantity=stock
            cart['pr' + id] = [quantity, name, desc, price, category, image];
        }else{
            quantityInput.value = newValue;
            cart[idstr][0] += delta;
            localStorage.setItem('cart', JSON.stringify(cart));
        }
        
    } else {
        delete cart[idstr]
        document.getElementById('quantity-controls-' + id).style.display = 'none';
        document.getElementById('pr' + id).style.display = 'inline-block';
    }
    var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
    document.getElementById('cartDisplay').innerHTML = total;
    console.log(cart);
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function clearCart(n) {
    localStorage.removeItem('cart');
    cart = {};
    var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
    document.getElementById('cartDisplay').innerHTML = total;
    submitForm();
}

function submitForm() {
    var csrfToken = getCookie('csrftoken');
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = '/shop/cart/';
    
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'cart';
    input.value = JSON.stringify(cart);

    var csrfInput = document.createElement('input');
    csrfInput.type = 'hidden';
    csrfInput.name = 'csrfmiddlewaretoken';
    csrfInput.value = csrfToken;
    
    form.appendChild(input);
    form.appendChild(csrfInput);
    document.body.appendChild(form);
    form.submit();
}

function applyFilter(filterType) {
    if (filterType === 'low-high') {
        // Sort products by price low to high
        products.sort((a, b) => a[0].price - b[0].price);
    } else if (filterType === 'high-low') {
        // Sort products by price high to low
        products.sort((a, b) => b[0].price - a[0].price);
    } else if (filterType === 'quantity') {
        // Sort products by quantity (if applicable)
        // Implement sorting logic based on quantity
    }
    // Re-render products based on the sorted order
    // Example: updateProductList(sortedProducts);
}

document.addEventListener('beforeunload', function (event) {
    submitForm();
});

function toggleDescription(element) {
    const description = element.previousElementSibling;
    const fullDescription = element.nextElementSibling;

    if (description.style.display === 'none') {
        description.style.display = '-webkit-box';
        fullDescription.style.display = 'none';
        element.textContent = '... more';
    } else {
        description.style.display = 'none';
        fullDescription.style.display = 'block';
        element.textContent = '... less';
    }
}

var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
document.getElementById('cartDisplay').innerHTML = total;
