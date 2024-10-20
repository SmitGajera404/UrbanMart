import os
import json
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from .models import Orders
from django.contrib.auth.models import User


def sendOutOfStockEmail(req,product):
    subject = 'Out of stock alert!'
    from_email = 'urbanmart2824@gmail.com'
    to = User.objects.get(username=product.seller).email
    text_content = ''
    html_string=f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Out of Stock Notification</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .email-container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            padding: 20px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }}
        h2 {{
            color: #333333;
            text-align: center;
        }}
        p {{
            color: #555555;
            line-height: 1.6;
        }}
        .product-details {{
            background-color: #f9f9f9;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .product-details p {{
            margin: 5px 0;
            color: #333333;
        }}
        .cta-button {{
            display: block;
            width: 100%;
            text-align: center;
            margin: 20px 0;
        }}
        .cta-button a {{
            text-decoration: none;
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
        }}
        .cta-button a:hover {{
            background-color: #0056b3;
        }}
        footer {{
            text-align: center;
            font-size: 12px;
            color: #aaaaaa;
            margin-top: 30px;
        }}
    </style>
</head>
<body>

    <div class="email-container">
        <h2>Product Out of Stock Notification</h2>

        <p>Dear {product.seller},</p>

        <p>We wanted to inform you that the following product has recently gone out of stock on our platform:</p>

        <div class="product-details">
            <p><strong>Product Name:</strong>{product.p_name}</p>
            <p><strong>Product ID:</strong>{product.id}</p>
        </div>

        <p>Please restock your inventory as soon as possible to ensure continued availability for buyers.</p>

        <p>If you no longer wish to sell this product or plan to discontinue it, you can request to unlist the product. To discontinue the product, click the link below:</p>

        <div class="cta-button">
            <a href="https://192.168.29.77/seller/discontinue/{product.id}" target="_blank">Discontinue Product</a>
        </div>

        <p>If you choose to discontinue, please note that any remaining inventory will need to be sold before the product is fully unlisted from our platform.</p>

        <p>If you have any further questions or need assistance, feel free to contact our support team.</p>

        <footer>
            &copy; 2024 UrbanMart. All rights reserved.
        </footer>
    </div>

</body>
</html>
'''
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_string, "text/html")
    msg.send()

def sendLowStockEmail(email,seller,product,threshold):
    subject = 'Low Stock Alert!'
    from_email = 'urbanmart2824@gmail.com'
    to = email
    text_content = ''
    html_string=f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Low Stock Alert</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            width: 100%;
            max-width: 650px;
            margin: 0 auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #007BFF;
            color: #ffffff;
            padding: 15px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            padding: 20px;
        }}
        .content p {{
            font-size: 16px;
            line-height: 1.5;
        }}
        .product-info {{
            margin: 20px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            background-color: #f9f9f9;
        }}
        .product-info table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .product-info td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        .product-info td:first-child {{
            font-weight: bold;
        }}
        .action-section {{
            margin-top: 20px;
        }}
        .action-section p {{
            font-size: 16px;
            line-height: 1.5;
        }}
        .button {{
            display: inline-block;
            padding: 12px 20px;
            color: #ffffff;
            background-color: #007BFF;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
            text-align: center;
            margin-top: 10px;
        }}
        .footer {{
            padding: 10px;
            text-align: center;
            background-color: #f1f1f1;
            border-top: 1px solid #ddd;
            border-radius: 0 0 8px 8px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Low Stock Alert</h1>
        </div>
        <div class="content">
            <p>Dear {seller},</p>
            <p>We wanted to bring to your attention that the stock levels for one of your products are critically low with respect to current demand. Below are the details of the product in question:</p>
            <div class="product-info">
                <table>
                    <tr>
                        <td>Product Name:</td>
                        <td>{product.p_name}</td>
                    </tr>
                    <tr>
                        <td>Category:</td>
                        <td>{product.category}</td>
                    </tr>
                    <tr>
                        <td>Current Stock:</td>
                        <td>{product.stock}</td>
                    </tr>
                    <tr>
                        <td>Supplier:</td>
                        <td>{seller}</td>
                    </tr>
                </table>
            </div>
            <p>The current stock is below the recommended threshold of {threshold}. We advise that you place a reorder with the supplier as soon as possible to prevent any disruptions in your supply chain.</p>
            <div class="action-section">
                <a href="http://192.168.29.77:8000/seller/refillInventory/{product.id}" class="button">refill stock</a>
            </div>
            <p>If you have any questions or need further assistance, please do not hesitate to contact our support team.</p>
            <p>Thank you for your prompt attention to this matter.</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 UrbanMart. All rights reserved.</p>
            <p><a href="mailto:urbanmart2824@gmail.com" style="color: #007BFF; text-decoration: none;">sgajera@gmail.com</a></p>
        </div>
    </div>
</body>
</html>
'''
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_string, "text/html")
    msg.send()
    print("msg send successfully")


def sendOrderPlacedMail(request, items, email, name, order_id):
    order = Orders.objects.get(id=order_id)
    html_string = f'''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Invoice</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: #f7f7f7;
            }}

            .invoice-box {{
                width: 100%;
                max-width: 800px;
                margin: 20px auto;
                padding: 20px;
                border: 1px solid #eee;
                background: #fff;
            }}

            h1 {{
                font-size: 20px;
                text-align: center;
                color: #333;
            }}

            .info-section {{
                margin-bottom: 20px;
            }}

            .info-section p {{
                margin: 5px 0;
                font-size: 12px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}

            table, th, td {{
                border: 1px solid #ddd;
            }}

            th, td {{
                padding: 8px;
                text-align: left;
                font-size: 12px;
            }}

            th {{
                background-color: #333;
                color: #fff;
            }}

            .total-section {{
                text-align: right;
                font-size: 14px;
                margin-top: 20px;
            }}

            .total-section p {{
                margin: 5px 0;
            }}
        </style>
    </head>
    <body>
        <div class="invoice-box">
            <h1>UrbanMart</h1>
            <div class="info-section">
                <p><strong>Address:</strong> {order.address_line.address}</p>
                <p><strong>City, State, Zipcode:</strong> {order.address_line.city}, {order.address_line.state}, {order.address_line.zip_code}</p>
                <p><strong>Order ID:</strong> {order.id}</p>
                <p><strong>Order Date:</strong> {order.timestamp}</p>
                <p><strong>Payment Type:</strong> UPI(Gpay)</p>
            </div>
            <table>
                <tr>
                    <th>Product Name</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Total</th>
                </tr>'''

    itemDict = json.loads(order.items_json)
    total = 0
    for id, item in itemDict.items():
        product_total = int(item[0]) * int(item[3])
        html_string += f'''<tr>
                    <td>{item[0]}</td>
                    <td>{item[1]}</td>
                    <td>{item[3]}</td>
                    <td>{product_total}</td>
                </tr>'''
        total += product_total

    html_string += f'''</tbody>
            </table>
            <div class="total-section">
                <p><strong>Net Total:</strong> {total}</p>
            </div>
        </div>
    </body>
    </html>'''

    pdf_path = os.path.join(settings.MEDIA_ROOT, 'invoices', f"invoice_{order.id}.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')


    subject = 'Order Placed'
    from_email = 'urbanmart2824@gmail.com'
    to = email
    text_content = 'Order Placed'
    download_link = request.build_absolute_uri(reverse('download_invoice', args=[order.id]))
    
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order Confirmation</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
            color: #333;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            text-align: center;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
        }}
        .header h1 {{
            margin: 0;
            color: #007bff;
        }}
        .content {{
            padding: 20px;
        }}
        .content h2 {{
            color: #007bff;
        }}
        .content p {{
            font-size: 16px;
            line-height: 1.5;
        }}
        .order-details {{
            margin: 20px 0;
            border-collapse: collapse;
            width: 100%;
        }}
        .order-details th, .order-details td {{
            border: 1px solid #e0e0e0;
            padding: 10px;
            text-align: left;
        }}
        .order-details th {{
            background-color: #f8f9fa;
        }}
        .order-details td {{
            background-color: #f4f4f4;
        }}
        .total {{
            font-weight: bold;
            text-align: right;
            padding-right: 10px;
        }}
        .footer {{
            text-align: center;
            padding: 10px 0;
            border-top: 1px solid #e0e0e0;
            margin-top: 20px;
        }}
        .footer p {{
            margin: 0;
            font-size: 14px;
            color: #666;
        }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>Thank You for Your Order!</h1>
        </div>
        <div class="content">
            <h2>Order Confirmation</h2>
            <p>Dear {name},</p>
            <p>Thank you for your purchase! We are excited to inform you that your order has been successfully placed.</p>
            <p><strong>Order ID:</strong> {order_id}</p>
            <table class="order-details">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Quantity</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>"""
    
    itemDict = json.loads(items)
    total = 0
    for id, item in itemDict.items():
        html_content += f"""<tr>
                        <td>{item[1]}</td>
                        <td>{item[0]}</td>
                        <td>Rs. {int(item[3]) * int(item[0])}</td>
                    </tr>"""
        total += int(item[3]) * int(item[0])
    html_content += f"""<tfoot>
                    <tr>
                        <td colspan="2" class="total">Total</td>
                        <td>Rs. {total}</td>
                    </tr>
                </tfoot>
            </table>
            <p>You can download your invoice <a href="{download_link}">here</a></p>
            <p>We will send you another email once your order has been shipped.</p>
            <p>If you have any questions, feel free to contact our support team.</p>
            <p>Best Regards,<br>The UrbanMart Team</p>
        </div>
        <div class="footer">
            <p>&copy; 2024 UrbanMart. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>

                        """
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print("msg send successfully")

def sendMailContactUs(name, to):
    subject = "Got Your Message"
    from_email = "urbanmart2824@gmail.com"
    text_content = "This is an Informative message."
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Thank You for Contacting Us</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                padding: 10px 0;
                border-bottom: 1px solid #dddddd;
            }}
            .header img {{
                max-width: 150px;
            }}
            .content {{
                padding: 20px;
            }}
            .content h1 {{
                color: #333333;
            }}
            .content p {{
                color: #666666;
                line-height: 1.6;
            }}
            .footer {{
                text-align: center;
                padding: 10px 0;
                border-top: 1px solid #dddddd;
                color: #aaaaaa;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <img src="https://via.placeholder.com/150" alt="Organization Logo">
            </div>
            <div class="content">
                <h1>Thank You for Contacting Us!</h1>
                <p>Dear {name},</p>
                <p>Thank you for reaching out to us through our Contact Us page. We have received your message and our team is currently reviewing it. We will get back to you as soon as possible.</p>
                <p>If your inquiry is urgent, please use the phone number listed below to talk to one of our staff members. Otherwise, we will reply to your message shortly.</p>
                <p>Thank you for your patience and understanding.</p>
                <p>Best regards,</p>
                <p>UrbanMart</p>
                <p>+91 9726730195</p>
                <p>urbanmart2824@gmail.com</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 [Your Organization's Name]. All rights reserved.</p>
                <p>[Your Organization's Address]</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
def sendOtpMail(to,otp):
    print(to,otp)
    subject = "OTP Verification!"
    from_email = "urbanmart2824@gmail.com"
    text_content = "OTP Verification"
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 50px auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                text-align: center;
                padding: 20px 0;
                border-bottom: 1px solid #eeeeee;
            }}
            .header h1 {{
                margin: 0;
                color: #333333;
            }}
            .content {{
                padding: 20px;
                text-align: center;
            }}
            .content p {{
                font-size: 16px;
                color: #333333;
            }}
            .otp {{
                font-size: 24px;
                font-weight: bold;
                color: #333333;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                border-top: 1px solid #eeeeee;
                color: #777777;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>OTP Verification</h1>
            </div>
            <div class="content">
                <p>Your One-Time Password (OTP) for UrbanMart login is:</p>
                <div class="otp">{ otp }</div>
                <p>Please enter this OTP to complete your verification process. This OTP is valid for the next 10 minutes.</p>
                <p>If you did not request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 UrbanMart. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>

    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    print('send success')
def sendInventoryTransferMail(to,username):
        subject = "Fulfillment Center Inventory Requirement"
        from_email = "urbanmart2824@gmail.com"
        text_content = "Fulfillment Center Inventory Requirement"
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fulfillment Center Inventory Requirement</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                }}
                .container {{
                    max-width: 800px;
                    margin: auto;
                    padding: 20px;
                }}
                .header {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin-bottom: 20px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">Notice to Sellers: Fulfillment Center Inventory Requirement</div>
                <div class="section">
                    Dear {username},
                </div>
                <div class="section">
                    Thank you for choosing to list your products on our ecommerce platform. To ensure a smooth and efficient order fulfillment process, please be aware of the following important requirement before listing your products:
                </div>
                <div class="section">
                    <strong>Fulfillment Center Inventory Requirement</strong>
                    <ol>
                        <li>
                            <strong>Mandatory Inventory Transfer</strong>: When you list a product on our website, you are required to transfer your entire inventory of that product to our designated fulfillment center. This policy ensures that all orders can be promptly and reliably processed and shipped to customers.
                        </li>
                        <li>
                            <strong>Seller Responsibility</strong>: It is the seller's responsibility to arrange and bear the cost of transporting their inventory to the fulfillment center. The fulfillment center address and detailed shipping instructions are provided below:
                            <p><strong>Fulfillment Center Address:</strong><br>
                        Plot No. 23, North Street<br>
        Near Harron Salon<br>
        Sector 22<Br>
        Gurgaon, Haryana 122015<br>
        India

                            <p><strong>Shipping Instructions:</strong></p>
                            <ul>
                                <li>Clearly label all boxes with your seller name and product listing ID.</li>
                                <li>Include a detailed packing list inside each shipment, specifying the contents and quantities.</li>
                                <li>Use sturdy, secure packaging to prevent damage during transit.</li>
                                <li>Shipments must be delivered between 9:00 AM and 5:00 PM, Monday to Friday.</li>
                                <li>Notify our Fulfillment Center team at +91 9726730195 at least 24 hours before your shipment arrives to ensure a smooth intake process.</li>
                            </ul>
                        </li>
                        <li>
                            <strong>Inventory Verification</strong>: Upon arrival, our fulfillment team will verify the quantity and condition of the inventory. Any discrepancies will be communicated to you immediately for resolution.
                        </li>
                        <li>
                            <strong>Listing Activation</strong>: Your product listing will only be activated and visible to customers once the inventory has been received and verified at the fulfillment center.
                        </li>
                        <li>
                            <strong>Stock Replenishment</strong>: You must ensure continuous availability of stock at the fulfillment center. Regularly monitor your inventory levels and proactively send additional stock to avoid stockouts and potential penalties.
                        </li>
                    </ol>
                </div>
                <div class="section">
                    We appreciate your cooperation in adhering to this policy, which is designed to enhance customer satisfaction and streamline our fulfillment operations. If you have any questions or require assistance with the inventory transfer process, please contact our Seller Support team.
                </div>
                <div class="footer">
                    Thank you for your attention to this matter.<br><br>
                    Best regards,<br>
                    UrbanMart<br>
                    Seller Support Team
                </div>
            </div>
        </body>
        </html>

        """
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
def sendInventoryTransferOnRefillStockMail(to,username):
        subject = "Fulfillment Center Inventory Transfer"
        from_email = "urbanmart2824@gmail.com"
        text_content = "Fulfillment Center Inventory Transfer"
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Action Required: Fulfillment Center Inventory Transfer</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: auto;
            padding: 20px;
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        .header {{
            font-size: 24px;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 20px;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .footer {{
            margin-top: 20px;
            font-size: 14px;
            color: #555;
        }}
        .important {{
            color: #dc3545;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">Action Required: Fulfillment Center Inventory Transfer</div>
        <div class="section">
            Dear {username},
        </div>
        <div class="section">
            Thank you for submitting your refill request for inventory. Please be advised that before we can process your request, you must first transfer your entire inventory for the listed products to our designated fulfillment center.
        </div>
        <div class="section">
            <strong>Fulfillment Center Inventory Transfer Process</strong>
            <ol>
                <li>
                    <strong>Mandatory Inventory Transfer:</strong> To ensure seamless order fulfillment, you are required to transfer your full inventory of the listed products to our fulfillment center.
                </li>
                <li>
                    <strong>Seller Responsibility:</strong> You are responsible for arranging and covering the cost of transporting your inventory to the fulfillment center. Here are the details:
                    <p><strong>Fulfillment Center Address:</strong><br>
                        Plot No. 23, North Street<br>
        Near Harron Salon<br>
        Sector 22<Br>
        Gurgaon, Haryana 122015<br>
        India
                    <ul>
                        <li>Clearly label all boxes with your seller name and product listing ID.</li>
                        <li>Include a detailed packing list inside each shipment, specifying the contents and quantities.</li>
                        <li>Use sturdy, secure packaging to prevent damage during transit.</li>
                        <li>Deliver shipments between 9:00 AM and 5:00 PM, Monday to Friday.</li>
                        <li>Notify our Fulfillment Center team at [Fulfillment Center Contact Email/Phone Number] at least 24 hours prior to your shipment's arrival for a smooth intake process.</li>
                    </ul>
                </li>
                <li>
                    <strong>Inventory Verification:</strong> Upon arrival, our team will verify the quantity and condition of the inventory. Any discrepancies will be communicated to you for resolution.
                </li>
                <li>
                    <strong>Listing Activation:</strong> Your product listings will be activated and visible to customers only after the inventory is received and verified at the fulfillment center.
                </li>
                <li>
                    <strong>Stock Replenishment:</strong> Regularly monitor your inventory levels and send additional stock as needed to avoid stockouts and penalties.
                </li>
            </ol>
        </div>
        <div class="section">
            <p class="important">Your product listings will not be processed until your inventory is transferred. Please follow the steps above to complete the transfer and ensure prompt processing of your refill request.</p>
            <p>If you have any questions or need assistance with the inventory transfer, please contact our Seller Support team at [Support Email/Phone Number].</p>
        </div>
        <div class="footer">
            Thank you for your prompt attention to this matter.<br><br>
            Best regards,<br>
            UrbanMart<br>
            Seller Support Team
        </div>
    </div>
</body>
</html>

        """
        
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()