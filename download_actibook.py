import os
import requests
from PIL import Image

output_pdf = os.path.expanduser("~/Downloads/R8保険診療の手引.pdf")
base_url = "https://files.actibookone.com/contents/22064/737697-20260520105630/images/1/{}.jpg"
query_params = "Policy=eyJTdGF0ZW1lbnQiOlt7IkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTc3OTUyNTE2M319fV19&Signature=SbpHwjgW3DLDVO8gmSKZX2MkQ2F6YZu5kNezbnjUQvennL7WRQIF4RAvtkGu8Bcxl-PfIOCPz3oXJhONopDyqhHIhJi9HY0NfHFQORWHXJqkMNSyhsnKbNjubC8V7k8r8AYZ2szFfUcb1-tOJtfZZHSfTgThZOBQbZvPAPTMY~1mVyRNb5lyZaIeB35Ca4h~kj926zt76FtJkoXOthQ0sd~swXFKJlcT0p0XekdcWgW17GDmCSo4lbn8agUEIchAlSDXSQdoYzXJFQ4LT-WkPhVDPVmRQXN7NYGD8xN3~bKNkOSlFzOB3-z4A4a52iTBwxjoWXDsowWeLfGM~Mr1UQ__&Key-Pair-Id=APKAJBZGQAONT53PE2FA"

images = []
download_dir = "downloaded_pages"
os.makedirs(download_dir, exist_ok=True)

total_pages = 484

for i in range(1, total_pages + 1):
    img_path = f"{download_dir}/{i}.jpg"
    if not os.path.exists(img_path):
        print(f"Downloading page {i}/{total_pages}...")
        res = requests.get(base_url.format(i) + "?" + query_params)
        if res.status_code == 200:
            with open(img_path, "wb") as f:
                f.write(res.content)
        else:
            print(f"Failed to download page {i}, status code {res.status_code}")
            break

print("All pages downloaded. Converting to PDF...")

image_list = []
first_image = None
for i in range(1, total_pages + 1):
    img_path = f"{download_dir}/{i}.jpg"
    if os.path.exists(img_path):
        try:
            img = Image.open(img_path).convert('RGB')
            if first_image is None:
                first_image = img
            else:
                image_list.append(img)
        except Exception as e:
            print(f"Failed to process image {i}: {e}")

if first_image:
    first_image.save(output_pdf, save_all=True, append_images=image_list)
    print(f"Successfully saved to {output_pdf}")
else:
    print("No images found to convert.")
