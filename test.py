from image_with_gpt import imageWithGPT
from PIL import Image

client = imageWithGPT(
  # api_key=""
)
res = client.get(
  image=Image.open("./man.jpg"),
  prompt="please tell me humans clothes color."
)

print(res)

