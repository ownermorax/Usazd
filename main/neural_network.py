import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer OPENROUTER_API_KEY_REPLACED",
    "Content-Type": "application/json",
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-OpenRouter-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },

  data=json.dumps({
    "model": "google/gemma-3-12b-it",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": input()
          },

        ]
      }
    ]
  })
)



if response.status_code == 200:
  res = response.json()
  ans = res['choices'][0]['message']['content']
  print("Ответ модели:")
  print(ans)