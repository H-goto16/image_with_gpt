from image_with_gpt import imageWithGPT
from PIL import Image

client = imageWithGPT(
  api_key=""
)
res = client.get(
  image=Image.open("./hamada.jpg"),
  prompt="Please extract this data from image. [height,age,gender,hair color,color of pants,Whether or not to wear a mask,Whether or not to wear glasses,Whether or not to wear a hat,color of pants,color of clothes,sleeve length] and please return array"

)

print(res)

