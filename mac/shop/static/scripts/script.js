var cart;
if (localStorage.getItem('cart') == null) {
    cart = {};
} else {
    cart = JSON.parse(localStorage.getItem('cart'));
}
console.log(cart);
function addToCart(id) {
    var idstr = 'pr' + id;
    var quantity = parseInt(document.getElementById("quantity" + id).value);

    if (cart[idstr] == undefined) {
        cart[idstr] = [quantity, '', '', '', '', ''];
    } else {
        cart[idstr][0] += quantity;
    }
    console.log(cart);
    localStorage.setItem('cart', JSON.stringify(cart));
    var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
    document.getElementById('cartDisplay').innerHTML = total;
}

function updateQuantityDirect(id,stock, name, desc, price, category, image) {
    
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
    // Define a JavaScript variable to store the authentication status
    function showQuantityControls(id, name, desc, price, category, image) {
        console.log('defined');
        
       if (isAuthenticated) {  // Use the JavaScript variable instead of Django template tag
            var idstr = 'pr' + id;
            document.getElementById('quantity-controls-' + id).style.display = 'inline';
            document.getElementById('pr' + id).style.display = 'none';
            cart[idstr] = cart[idstr] == undefined ? [1, name, desc, price, category, image] : [cart[idstr][0], name, desc, price, category, image];
            document.getElementById('quantity' + id).value = cart[idstr][0];
            localStorage.setItem('cart', JSON.stringify(cart));
            var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
            document.getElementById('cartDisplay').innerHTML = total;
            console.log(cart);
            try {
                $('#cart-user').val(JSON.stringify(cart));
            } catch (error) {
                console.log(error);
            }
        } else {
            $('#signInModal').modal('show');
        }
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

var total = Object.values(cart).reduce((sum, value) => sum + value[0], 0);
document.getElementById('cartDisplay').innerHTML = total;

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
