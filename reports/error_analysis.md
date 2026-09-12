# Error analysis - which product types confuse the model?

Test images: **3114** | misclassified: **258** (8.29%)

> Sub-category names marked *(title-derived)* come from product titles:
the corpus's Amazon-Fashion slice ships without a category tree
(`categories == []` upstream), so Apparel sub-categories are derived
from titles with a transparent keyword rule.

## Misclassified volume per pair

| true -> predicted | count | % of that true class in test |
|---|---|---|
| Electronics -> Home | 68 | 6.6% |
| Home -> Electronics | 63 | 6.0% |
| Apparel -> Home | 51 | 5.0% |
| Apparel -> Electronics | 37 | 3.6% |
| Home -> Apparel | 24 | 2.3% |
| Electronics -> Apparel | 15 | 1.4% |

## Top sub-categories behind each confusion pair

### Apparel -> Electronics  (37 images)

- **Jewelry & Watches (title-derived)** - 14 images, e.g. *"SUPERDAVES SUPERSTORE Kurdistan Red Country Flag C' Bracelet Wristband. for Adults & Teens"*
- **Other apparel (title-derived)** - 9 images, e.g. *"Magnetic Backgammon Board Game"*
- **Shoes (title-derived)** - 3 images, e.g. *"Paw Patrol Skye & Everest Toddler Girls Slippers, Medium (7/8)"*
- **Belts & Accessories (title-derived)** - 3 images, e.g. *"niceeshop(TM) Unisex Soft Wool Classic Braid Knit Infinity Warm Loop Scarf Hood -Grey"*
- **Bags & Wallets (title-derived)** - 2 images, e.g. *"Abillon Travel Toiletry Bag Leather Shaving Dopp Kit, Unisex"*
- **Hats & Caps (title-derived)** - 2 images, e.g. *"G-od is Good All The Time Filter Pocket Washable Reusable Face ma-sk Balaclava Bandanas wi"*
- **Wristbands & Straps (title-derived)** - 2 images, e.g. *"Amzpas Metal Replacement Bands Compatible with Fitbit Charge 2 Bands, Adjustable Stainless"*
- **Shirts & Tops (title-derived)** - 2 images, e.g. *"Giraffe Cute Universal 11.6" 12" 12.1" inch Neoprene Tablet Laptop Soft Sleeve Bag Cover C"*

### Apparel -> Home  (51 images)

- **Other apparel (title-derived)** - 17 images, e.g. *"Pierced Owl - Organic Coconut Wood Saddle Fit Solid Plugs, Sold as a Pair"*
- **Jewelry & Watches (title-derived)** - 7 images, e.g. *"10K Yellow Gold Cherub Angel Pendant Praying Angel 1 inch"*
- **Bags & Wallets (title-derived)** - 5 images, e.g. *"S.CHU Women's A Mom And A Nurse Tote Handbag Stripes Weave Shoulder Bag Black"*
- **Hats & Caps (title-derived)** - 4 images, e.g. *"4 Pack Santa Hat with Holiday Glasses, Christmas Santa Hat for Kids, Toddler Santa Velvet "*
- **Shoes (title-derived)** - 3 images, e.g. *"Round Shoelaces [3 Pairs] 5/32" Thick - For Shoes, Sneakers & Boots - By ACCOTCOLE (48" (1"*
- **Dresses (title-derived)** - 3 images, e.g. *"Women Fashion V-Neck 3/4 Sleeve Long Length Print Lace Dress Plus Size XXL-XXXXL"*
- **Socks & Hosiery (title-derived)** - 3 images, e.g. *"canFly Men's 6-Pack Crew Thin Cotton Socks 9-11 (Black)"*
- **Wristbands & Straps (title-derived)** - 3 images, e.g. *"Barsty Men's Breathable Ice Silk Jock Strap S 4-Pack Red/Light Blue/White/Black"*

### Electronics -> Apparel  (15 images)

- **Wearable Technology** - 3 images, e.g. *"VANLUCK Strap Compatible with Mi Band 5/XiaoMi Band 6, Replacement Leather Strap Wristband"*
- **Computers & Accessories** - 3 images, e.g. *"hBARSCI Violin Player Vinyl Decal - 5 Inches - for Cars, Trucks, Windows, Laptops, Tablets"*
- **Television & Video** - 2 images, e.g. *"Power Acoustik PMD-103CM BG 10.4-Inch Overhead Monitor with Built-in DVD Player"*
- **Accessories & Supplies** - 2 images, e.g. *"Brady Men's Run Short Sleeve"*
- **Headphones, Earbuds & Accessories** - 2 images, e.g. *"Gig Em Aggies Texas A&M Thumb T-Shirt"*
- **Car & Vehicle Electronics** - 1 images, e.g. *"HTTMT HL1584-052F-R/L- Speaker Pod Box 6.5 Inches Compatible with 1993-2013 Harley Touring"*
- **Camera & Photo** - 1 images, e.g. *"Photojojo Cell Lenses for Apple iPhones and Android Phones,Pack of 3(Includes Fisheye, Tel"*
- **Unknown** - 1 images, e.g. *"Deokke Kids Teens Blue Light Blocking Glasses for Girls Boys,Computer Gaming Glasses for K"*

### Electronics -> Home  (68 images)

- **Computers & Accessories** - 17 images, e.g. *"1080P Webcam with Microphone, Computer USB Web Camera Full HD for Windows 10 8 7 XP Mac OS"*
- **Unknown** - 13 images, e.g. *"EOS Meraki MX60 Enterprise License and Support, 3 Years, Electronic Delivery"*
- **Camera & Photo** - 11 images, e.g. *"MyRingLight - Fluorescent Ring Light, 5400K, 65watts, Photo and Video"*
- **Home Audio** - 5 images, e.g. *"Theater Solutions TS65W in Wall 6.5" Speakers Surround Sound Home Theater 2 Pair Pack"*
- **Portable Audio & Video** - 4 images, e.g. *"Outdoor Dog Supply Reflective Glow Tuff Long Range Collar Antennas for the Garmin Dc30 & D"*
- **Accessories & Supplies** - 4 images, e.g. *"Pace DSL FILTER for TELEPHONE ,FAX & ANALOG MODEMS-A packet of 4"*
- **Headphones, Earbuds & Accessories** - 4 images, e.g. *"Trackeroo - Portable AirPods Case - Expandable Pouch Doubles as a Tracking Tile Case - Dur"*
- **Television & Video** - 3 images, e.g. *"HR-6010 TailTwister Rotator Plates for use on Glen Martin Hazer H-2 / H-3 / H-4 Trams"*

### Home -> Apparel  (24 images)

- **Home Décor Products** - 9 images, e.g. *"Juvale Blue Nautical Poop Deck Hanging Wall Sign Beach Ocean Theme (12 x 7.5 In)"*
- **Kitchen & Dining** - 6 images, e.g. *"YUTRO Fashion Women's Winter Slouchy Fleece Lined Wool Beanie Hat One Size OCEAN BLUE"*
- **Vacuums & Floor Care** - 2 images, e.g. *"Oreck Belt, Corded U7000 Series"*
- **Event & Party Supplies** - 2 images, e.g. *"9th Birthday, 9th Birthday Gifts, 9th Birthday Bracelet for Girls, 9th Birthday Necklace f"*
- **Storage & Organization** - 1 images, e.g. *"BRAMING 82L Large Laundry Basket , Collapsible fabric Laundry Hamper with Handles, Foldabl"*
- **Bedding** - 1 images, e.g. *"HollyHOME Luxury Silky Soft 2 Pieces of Satin Pillowcases for Hair Cool, Queen Size Cabbag"*
- **Seasonal Décor** - 1 images, e.g. *"THE APRONPLACE Red Plush Personalized Christmas Stocking"*
- **Bath** - 1 images, e.g. *"Loomin Rustproof Roller Shower Curtain Rings Double Glide Hooks,12 Count (Chrome)"*

### Home -> Electronics  (63 images)

- **Kitchen & Dining** - 22 images, e.g. *"De'Longhi Stilosa Manual Espresso Machine, Latte & Cappuccino Maker & Stainless Steel Milk"*
- **Home Décor Products** - 11 images, e.g. *"Karlsson Wall Clock Platinum Record Aluminum, Silver"*
- **Unknown** - 9 images, e.g. *"Grocery plastic Bag Dispenser,Brushed Stainless Steel Organizer,Wall Mount Trash Holder,Re"*
- **Vacuums & Floor Care** - 5 images, e.g. *"EFP Vacuum Cleaner Suction Hose Attachment Pipe | Grey | 6' Length with 1-1/2" Diameter | "*
- **Heating, Cooling & Air Quality** - 5 images, e.g. *"RIGOGLIOSO True HEPA Air Purifier Filter Replacement Compatible for Home Ionic Air Purifie"*
- **Bath** - 4 images, e.g. *"Toothbrush Holder Wall Mounted, Heasa Animal Kids Toothbrush Holder (White Bear)"*
- **Bedding** - 2 images, e.g. *"Astralign Office Chair Back Support Pillow: USA Made Thoracic Back Pillow for Back Pain & "*
- **Storage & Organization** - 2 images, e.g. *"Martha Stewart Living 32 in. Closet System Rail"*
