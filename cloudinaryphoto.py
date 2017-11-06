import cloudinary.uploader
#import cloudinary
#import re
#from PIL import Image
#from PIL import Image
#import urllib.request





cloudinary.uploader.upload("temp.jpg", public_id="boiiiii",api_key=156733677359362, api_secret="gUf5tbocYS8dZvA94bps3f_ALNE", cloud_name="projecteve", version="v1507590682")#, use_filename=True, unique_filename=False)

"""
result = str(cloudinary.api.resources(cloud_name="projecteve", api_key=156733677359362, api_secret="gUf5tbocYS8dZvA94bps3f_ALNE"))
try:
    result = re.compile("'version': (.*?),", re.DOTALL |  re.IGNORECASE).findall(result)[0]
except:
    pass
URL = "http://res.cloudinary.com/projecteve/image/upload/v" + result + "/boiiiii.png"
image = cloudinary.CloudinaryImage(URL).image(type="fetch", cloud_name="projecteve", api_key=156733677359362, api_secret="gUf5tbocYS8dZvA94bps3f_ALNE")

print(type(image))
print(image)
"""

'''
URL = 'http://res.cloudinary.com/projecteve/image/upload/v1507252167/boiiiii.png'

with urllib.request.urlopen(URL) as url:
    with open('temp.jpg', 'wb') as f:
        f.write(url.read())

img = Image.open('temp.jpg')

img.show()

print(type(img))
'''