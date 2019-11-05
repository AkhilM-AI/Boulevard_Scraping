import csv
import json
import urllib.request as ur
from bs4 import BeautifulSoup

# Function to extract data for each page
def get_page(page):
    data = ur.urlopen(url + '?limit={}&page={}'.format(250,page)).read()
    products = json.loads(data)['products']
    return products

#Function to extract Details about product from body_html
def detail_html(product):
    body_html=product['body_html']
        #preserving newlines and bullet points for ul elements
    if body_html.find('<li') >=0 and body_html.find('/li>') >=0: 
        Details = body_html[body_html.index('<li'):body_html.rfind('/li>')+4]
        Details_Formatted = Details[Details.index('<li'):Details.rfind('/li>')+4]
    else:
        #if body_html isn't in default html format , then storing as text
        soup = BeautifulSoup(body_html)
        data = soup.findAll(text=True)
        Details_Formatted =''.join([str(line) if len(line)>1 else'' for line in data])
    return Details_Formatted

#Function to findout fit model and sizes available
def fit_size(product):
    fit= [s.split(':')[-1] for s in product['tags'] if "fit" in s]
    size = ([s['values'] for s in product['options'] if s['name']=='Size']+[''])[0]
    Size_and_fit =" Fit is "+( ','.join(fit) if len(fit) >= 1 else '')  + " and Sizes available : " +','.join(size)
    return  Size_and_fit        

#Function to format description as required
def Description_format(Details,Size_fit,Shipping_Returns):
    Description ="""<sections><section id="1"><sectionTitle>Details</sectionTitle><sectionBody>""" +Details+""" </sectionBody></section><section id="2"><sectionTitle>Size &amp; Fit</sectionTitle><sectionBody><li><span>"""+ Size_fit +"""</span></li></sectionBody></section><section id="3"><sectionTitle>Shipping &amp; Returns</sectionTitle><sectionBody><li><span>""" + Shipping_Returns +"""</span></li></sectionBody></section></sections>"""
    
    return Description

# main function
if __name__ == "__main__":                         
    # Brand url
    brand_name ="outerknown"
    base_url = "https://www."+brand_name+".com"
    url = base_url + '/products.json'
    
    with open('products.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        output_columns =['Collection' ,'Handle' ,'Title' ,'Body (HTML)' ,'Vendor' ,'Type' ,'Tags' ,'Published' ,'Option1 Name' ,'Option1 Value' ,'Option2 Name' ,'Option2 Value' ,'Option3 Name' ,'Option3 Value' ,'Variant SKU' ,'Variant Grams' ,'Variant Inventory Tracker' ,'Variant Inventory Policy' ,'Variant Fulfillment Service' ,'Variant Price' ,'Variant Compare At Price' ,'Variant Requires Shipping' ,'Variant Taxable' ,'Variant Barcode' ,'Image Src' ,'Image Position' ,'Image Alt Text' ,'Gift Card' ,'SEO Title' ,'SEO Description' ,'Google Shopping / Google Product Category' ,'Google Shopping / Gender' ,'Google Shopping / Age Group' ,'Google Shopping / MPN' ,'Google Shopping / AdWords Grouping' ,'Google Shopping / AdWords Labels' ,'Google Shopping / Condition' ,'Google Shopping / Custom Product' ,'Google Shopping / Custom Label 0' ,'Google Shopping / Custom Label 1' ,'Google Shopping / Custom Label 2' ,'Google Shopping / Custom Label 3' ,'Google Shopping / Custom Label 4' ,'Variant Image' ,'Variant Weight Unit' ,'Variant Tax Code' ,'Cost per item' ]
        writer.writerow(output_columns)
        page = 1
        products = get_page(page)
        # While loop ends, when it explores are pages 
        while products:
            for product in products:
                #Ignoring the products that contain the string “gift” in either their title, handle, or product_type fields
                if ('gift' in (product['title'].lower() + product['handle'].lower()+ product['product_type'].lower())):
                    continue
                
                #Extracting gender from 'tags' and if not found assiging 'unisex'
                gender =''.join([s.split(':')[-1] for s in product['tags'] if "gender" in s])
                Vendor= brand_name + "-"+ gender[:-1] if len(gender) > 1 else 'unisex'
                
                #Handle and Title
                handle = product['handle']
                title = product['title'].upper()
                product_url = base_url + '/products/' + product['handle']
                category = product['product_type'] 
                
                #Extracting Details about product from body_html
                Details_Formatted = detail_html(product)         
                Shipping_Returns = "Free shipping on order over $100 and  30-day returns on purchase as long as they are in original condition (unworn, unwashed and with tags)."
                
                #Fit type and sizes available
                Size_fit=fit_size(product)
                
                #Description(Body Html) in required format
                Description = Description_format(Details,Size_fit,Shipping_Returns)
                
                #tags for the product based on brand name + style of product + Product_type
                tags = [brand_name.lower()]+ [category] + [s.split(':')[-1] for s in product['tags'] if "style" in s and s.split(':')[-1] not in [category]]
                tags = ','.join(tags)
                
                #Using price of one of the variants
                variant=product['variants'][0]
                price = variant['price']
                 
                images_url = []
                image_position=[]
                for images in product['images']:
                    images_url.append(images['src'])
                    image_position.append(images['position'])
                    if images['position']==1:
                        row = [Vendor,handle,title,Description,Vendor,title,tags,'','Title',' Default Title','Link',product_url,'','','',1,'','deny','manual',price,'','','','',images['src'],images['position'],'','FALSE']
                        writer.writerow(row)
                    else:
                        row = [Vendor,handle,'','','','','','','','','','','','','','','','','','','','','','',images['src'],images['position'],'','']
                        writer.writerow(row)
            page += 1
            products = get_page(page)