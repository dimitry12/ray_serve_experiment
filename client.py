import requests

input_text = "Once upon a time"

response = requests.post("http://127.0.0.1:8000/", json=input_text)
output_text = response.text

print(output_text)
