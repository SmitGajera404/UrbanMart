from django.shortcuts import render
from django.http import HttpResponse
def index(req):
    return HttpResponse("""

    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UrbanMart-Main page</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" integrity="sha384-xOolHFLEh07PJGoPkLv1IbcEPTNtaed2xpHsD9ESMhqIYd0nLMwNLD69Npy4HI+N" crossorigin="anonymous">
    <style>
        .link-card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.link-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.card-body i {
  font-size: 48px;
  color: #007bff;
  margin-bottom: 15px;
}

@media (max-width: 767px) {
  .card-body i {
    font-size: 36px;
  }
}

    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row text-center">
          <!-- Shop Card -->
          <div class="col-md-4">
            <a href="/shop/" class="card link-card">
              <div class="card-body">
                <i class="fas fa-shopping-cart"></i>
                <h5 class="card-title">Shop</h5>
                <p class="card-text">Explore and purchase products</p>
              </div>
            </a>
          </div>
          
          <!-- Seller Card -->
          <div class="col-md-4">
            <a href="/seller/" class="card link-card">
              <div class="card-body">
                <i class="fas fa-store"></i>
                <h5 class="card-title">Seller</h5>
                <p class="card-text">Manage your product listings</p>
              </div>
            </a>
          </div>
          
          <!-- Warehouse Card -->
          <div class="col-md-4">
            <a href="/warehouse/" class="card link-card">
              <div class="card-body">
                <i class="fas fa-warehouse"></i>
                <h5 class="card-title">Warehouse</h5>
                <p class="card-text">Track inventory and orders</p>
              </div>
            </a>
          </div>
        </div>
      </div>
      
</body>
</html>
""")