var cart;
if (localStorage.getItem('cart') == null) {
    cart = {}
} else {
    cart = JSON.parse(localStorage.getItem('cart'))
}
function toggleReplyForm(id) {
    var replyForm = document.getElementById(id);
    if (replyForm.style.display === 'none') {
        replyForm.style.display = 'block';
    } else {
        replyForm.style.display = 'none';
    }
}
function addlike(total, sno, netTotal, mode) {
    if (isAuthenticated) {
        if ($('#like' + `-${sno}`).hasClass('text-info')) {

        } else {
            $('#like' + `-${sno}`).html('<i class="fas fa-thumbs-up"></i>' + (parseInt($('#like' + `-${sno}`).text()) + 1));
            if (mode == 'disliked') { $('#dislike' + `-${sno}`).html('<i class="fas fa-thumbs-down"></i>' + (netTotal - 1)); }
            else {
                $('#dislike' + `-${sno}`).html('<i class="fas fa-thumbs-down"></i>' + (netTotal));
            }
            $('#like' + `-${sno}`).on('click', null);
            $('#like' + `-${sno}`).addClass('text-info');
            $('#like' + `-${sno}`).removeClass('text-dark');
            $('#dislike' + `-${sno}`).removeClass('text-danger');
            $('#dislike' + `-${sno}`).addClass('text-dark');

            var formData = {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'sno': sno
            };

            $.ajax({
                url: '/shop/like/',
                data: formData,
                type: 'POST',
                dataType: 'json',
                encode: true,
                success: function (data) { }
            })
        }
    }
    else {
        $('#signInModal').modal('show');
    }
}
function adddislike(total, sno, netTotal, mode) {
    if (isAuthenticated) {
        if ($('#dislike' + `-${sno}`).hasClass('text-danger')) {

        } else {

            if (mode == 'liked') {
                $('#like' + `-${sno}`).html('<i class="fas fa-thumbs-up"></i>' + (netTotal - 1));
            }
            else {
                $('#like' + `-${sno}`).html('<i class="fas fa-thumbs-up"></i>' + (netTotal));
            }
            $('#dislike' + `-${sno}`).html(
                '<i class="fas fa-thumbs-down"></i>' + (parseInt($('#dislike' + `-${sno}`).text()) + 1));
            $('#dislike' + `-${sno}`).on('click', null);
            $('#dislike' + `-${sno}`).addClass('text-danger');
            $('#dislike' + `-${sno}`).removeClass('text-dark');
            $('#like' + `-${sno}`).removeClass('text-info');
            $('#like' + `-${sno}`).addClass('text-dark');

            var formData = {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'sno': sno
            };

            $.ajax({
                url: '/shop/dislike/',
                data: formData,
                type: 'POST',
                dataType: 'json',
                encode: true,
                success: function (data) { }
            })
        }
    } else {
        $('#signInModal').modal('show');
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const stars = document.querySelectorAll('.star-rating .star');
    const ratingInput = document.getElementById('rating');

    stars.forEach(star => {
        star.addEventListener('click', function () {
            const value = this.getAttribute('data-value');
            ratingInput.value = value;

            stars.forEach(s => {
                if (s.getAttribute('data-value') <= value) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });
});
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

function updateQuantityDirect(id, stock, name, desc, price, category, image) {

    var quantity = parseInt(document.getElementById('quantity' + id).value);
    stock = parseInt(stock);
    if (quantity > 0) {
        if (quantity > stock) {
            alert("Sorry, we only have " + stock + " in stock of " + name);
            document.getElementById('quantity' + id).value = stock;
            quantity = stock
            cart['pr' + id] = [quantity, name, desc, price, category, image];
        } else {
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
function showQuantityControls(id, name, desc, price, category, image) {

    if (isAuthenticated) {
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
            $('#cart-user').val(JSON.stringify(cart))
        } catch (error) {
            console.log(error);
        }
    } else {
        $('#signInModal').modal('show');
    }
}

function updateQuantity(id, stock, name, desc, price, category, image, delta) {
    var idstr = 'pr' + id;
    stock = parseInt(stock);
    var quantityInput = document.getElementById("quantity" + id);
    console.log("Update q");
    var newValue = parseInt(quantityInput.value) + delta;
    if (newValue > 0) {
        if (newValue > stock) {
            alert("Sorry, we only have " + stock + " in stock of " + name);
            document.getElementById('quantity' + id).value = stock;
            quantity = stock
            cart['pr' + id] = [quantity, name, desc, price, category, image];
        } else {
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
