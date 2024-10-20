
import io
import folium.features
import folium.map
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
from django.http import HttpResponse
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from shop.models import *
from seller.models import *
import seaborn as sns
import pandas as pd
import imgkit
import folium
import numpy as np
import pytz
import datetime

def plot_sales_data(req):
    # Example sales data

    products=Product.objects.filter(seller=req.user.username,lifetime_sales__gt=0)
    sales_products=[]
    sales_data=[]
    for i in products:
        sales_products.append(i.p_name[:6:]+"...")
        sales_data.append(i.lifetime_sales)

    # Create a figure with 2 subplots (1 row, 2 columns)
    fig = Figure(figsize=(25,5))
    ax = fig.add_subplot(1, 1, 1)

    # First subplot (same as original)
    ax.bar(sales_products, sales_data)
    ax.set_title('Sales Over Time')
    ax.set_xlabel('Products')
    ax.set_ylabel('Sales')

    # Adjust layout
    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as a response
    return HttpResponse(buffer.getvalue(), content_type='image/png')
def plot_sales_order(req):
    products=Product.objects.filter(seller=req.user.username,lifetime_sales__gt=0)
    p_names=[]
    lifetime_sales=[]
    order_no=[]
    for i in products:
        if i.lifetime_sales>0:
            p_names.append(i.p_name[0:10:]+'...')
            lifetime_sales.append(i.lifetime_sales)
            count=Orders.objects.filter(items_json__icontains='"pr'+str(i.id)+'":').count()
            order_no.append(count)

    fig = Figure(figsize=(15,5))
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(lifetime_sales,order_no)

    for i in p_names:
        ax.annotate(i, (lifetime_sales[p_names.index(i)],order_no[p_names.index(i)]),textcoords="offset points", xytext=(10,-10), ha='center', fontsize=10, color='red')

    ax.set_title('Sales Order Ratio')
    ax.set_xlabel('Lifetime sales')
    ax.set_ylabel('Total number of orders')

    # Adjust layout
    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def top_5_best_sellers(req):

    products=Product.objects.filter(seller=req.user.username).order_by('-lifetime_sales')
    sales_products=[]
    sales_data=[]
    for i in products[0:5]:
        sales_products.append(i.p_name[:16:]+"...")
        sales_data.append(i.lifetime_sales)

    fig = Figure(figsize=(10,5))
    ax = fig.add_subplot(1, 1, 1)

    ax.bar(sales_products, sales_data)
    ax.set_title('Top 5 Best Sellers')
    ax.set_xlabel('Products')
    ax.set_ylabel('Sales')

    # Adjust layout
    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as a response
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def revenue_contrib_category(req):
    categoricalSales = CategoricalRevenue.objects.filter(user=req.user)
    revenue = []
    category = []
    for i in categoricalSales:
        revenue.append(i.revenue)
        category.append(i.category+f" (₹{i.revenue})")
    
    fig = Figure(figsize=(10,5))
    ax = fig.add_subplot(1, 1, 1)

    ax.pie(revenue, labels=category, autopct='%1.1f%%')
    ax.set_title('Categorical Revenue Contribution')
    # Adjust layout
    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as a response
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def view_to_order_funnel(req):
    stages = ["Product page visits", "No. of Orders"]
    numbers = []
    products=Product.objects.filter(seller=req.user.username)
    sum=0
    count=Orders.objects.filter(sellers__icontains='"'+req.user.username+'"').count()
    for i in products:
        sum+=i.views
    numbers.append(sum)
    numbers.append(count)
    stages.reverse()
    numbers.reverse()

    fig = Figure(figsize=(10,5))
    ax = fig.add_subplot(1, 1, 1)

    for i, (stage, number) in enumerate(zip(stages, numbers)):
        ax.barh(stage, number, color='skyblue', edgecolor='black')

    ax.set_title('Sales Funnel')
    ax.set_xlabel('Number of Customers')
    ax.set_ylabel('Stage')

    fig.tight_layout()

    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def order_volume_by_day(req):

    orders=Orders.objects.filter(sellers__icontains='"'+req.user.username+'"')
    data = np.zeros((7, 24))
    ist=pytz.timezone('Asia/Kolkata')
    day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
    }


    for order in orders:
        update = OrderUpdate.objects.filter(order_id=order.id, update_desc__icontains="placed").first()

        if update:

            timestamp_utc = update.timestamp
            timestamp_ist = timestamp_utc.astimezone(ist)

            day_of_week = timestamp_ist.strftime("%A")
            hour_of_day = int(timestamp_ist.strftime("%H"))

            day_index = day_mapping[day_of_week]

            data[day_index][hour_of_day] += 1
    hours = ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM',
             '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    
    
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(data, ax=ax, xticklabels=hours, yticklabels=days, cmap='coolwarm', fmt='d')

    # Add titles and labels
    ax.set_title('Order Volume by Time of Day')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Day of Week')

    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as an HTTP response
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def plot_sales_trend(req,product):
    try:
        dailySales=DailySales.objects.filter(product=product)
    except:
        return HttpResponse("https://i.pinimg.com/originals/49/e5/8d/49e58d5922019b8ec4642a2e2b9291c2.png")
    todayDate=datetime.date.today()
    sales=[]
    dates=[]
    for i in range(7):
        date=todayDate-datetime.timedelta(days=i)
        dates.append(date)
        try:
            sale = dailySales.get(date=date).sales
        except:
            sale = 0
        sales.append(sale)
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)    
    ax.plot(dates, sales, marker='o')
    ax.set_title("Sales TrendLine")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def order_volume(req,product):
    try:
        orders=Orders.objects.filter(items_json__icontains = '"pr' + str(product.id) + '"')
    except:
       return HttpResponse("https://i.pinimg.com/originals/49/e5/8d/49e58d5922019b8ec4642a2e2b9291c2.png")
    data = np.zeros((7, 24))
    ist=pytz.timezone('Asia/Kolkata')
    day_mapping = {
    'Monday': 0,
    'Tuesday': 1,
    'Wednesday': 2,
    'Thursday': 3,
    'Friday': 4,
    'Saturday': 5,
    'Sunday': 6
    }


    for order in orders:
        update = OrderUpdate.objects.filter(order_id=order.id, update_desc__icontains="placed").first()

        if update:

            timestamp_utc = update.timestamp
            timestamp_ist = timestamp_utc.astimezone(ist)

            day_of_week = timestamp_ist.strftime("%A")
            hour_of_day = int(timestamp_ist.strftime("%H"))

            day_index = day_mapping[day_of_week]

            data[day_index][hour_of_day] += 1
    hours = ['12 AM', '1 AM', '2 AM', '3 AM', '4 AM', '5 AM', '6 AM', '7 AM', '8 AM', '9 AM', '10 AM', '11 AM',
             '12 PM', '1 PM', '2 PM', '3 PM', '4 PM', '5 PM', '6 PM', '7 PM', '8 PM', '9 PM', '10 PM', '11 PM']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    
    
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot(1, 1, 1)
    sns.heatmap(data, ax=ax, xticklabels=hours, yticklabels=days, cmap='coolwarm', fmt='d')

    # Add titles and labels
    ax.set_title('Order Volume by Time of Day')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Day of Week')

    fig.tight_layout()

    # Convert plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as an HTTP response
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def sales_distribution(req,product):
    try:
        orders=Orders.objects.filter(items_json__icontains = '"pr' + str(product.id) + '"')
    except:
        return HttpResponse("https://i.pinimg.com/originals/49/e5/8d/49e58d5922019b8ec4642a2e2b9291c2.png")
    india_map=folium.Map(location=[20,77],zoom_start=4)
    orderLocations = folium.FeatureGroup()

    csv_f=pd.read_csv('cities.csv')
    for order in orders:
        lat = csv_f[(csv_f["name"] == order.address_line.city)].latitude
        lon = csv_f[(csv_f["name"] == order.address_line.city)].longitude
        orderLocations.add_child(folium.features.CircleMarker([lat,lon],radius=5,color='red',fill=True))
    india_map.add_child(orderLocations)
    map_html = india_map._repr_html_()
    return map_html

    

def word_freq(req, product):
    try:
        reviews = ProductReview.objects.filter(product=product)
    except:
        return HttpResponse("https://i.pinimg.com/originals/49/e5/8d/49e58d5922019b8ec4642a2e2b9291c2.png")

    allReviewString = ""
    for review in reviews:
        allReviewString += review.review + " "
    
    review_wc = WordCloud(stopwords=set(STOPWORDS))
    review_wc.generate(allReviewString)
    
    # Create a figure
    fig = Figure(figsize=(10, 8))
    ax = fig.add_subplot(1, 1, 1)
    
    # Plot the word cloud on the figure
    ax.imshow(review_wc, interpolation='bilinear')
    ax.axis('off')
    fig.tight_layout()
    # Convert the plot to PNG image
    buffer = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)

    # Return the image as an HTTP response
    return HttpResponse(buffer.getvalue(), content_type='image/png')

