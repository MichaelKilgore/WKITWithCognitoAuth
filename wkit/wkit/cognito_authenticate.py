import json
import base64
import requests
from django.shortcuts import redirect
from django.http import HttpResponse

client_id = "19shq1tf1n191fqqtsbc02kl25"
client_secret = "1rr142l6gvkc2e8k6n4740hm7im70gr9kimc4n0uip86uoljv2kv"

token_url = "https://simpledemodomain123.auth.us-west-2.amazoncognito.com/oauth2/token"
redirect_uri = 'https://yw1cjkg64a.execute-api.us-west-2.amazonaws.com/test/website'

message = bytes(f"{client_id}:{client_secret}",'utf-8')
secret_hash = base64.b64encode(message).decode()

login_link = "https://simpledemodomain123.auth.us-west-2.amazoncognito.com/login?client_id=19shq1tf1n191fqqtsbc02kl25&response_type=code&scope=aws.cognito.signin.user.admin+email+openid+phone+profile&redirect_uri=https://q01n0a56w6.execute-api.us-west-2.amazonaws.com/test/test"


def cog_auth(func):
  def wrapper(*args, **kwargs):
    if len(args) > 0: # valid function check
      request = args[0]
      if "code" in request.GET: # create token and add as cookie.
        code = request.GET.get('code', '')
        payload = {
          "grant_type": 'authorization_code',
          "client_id": client_id,
          "code": code,
          "redirect_uri": 'https://q01n0a56w6.execute-api.us-west-2.amazonaws.com/test/test'
        }        
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {secret_hash}"}
        resp = requests.post(token_url, params=payload, headers=headers)
        if "id_token" in resp.json():
          response = func(*args, **kwargs)
          response.set_cookie('Authorization', resp.json()["id_token"])
          
          return response
        else:
          return HttpResponse('Unauthorized: no id_token in return: '+str(resp.json()), status=401)

      elif "Authorization" in request.COOKIES: # authorize cookie is valid and not expired or whatever.
        auth = request.COOKIES["Authorization"]
        r = requests.get(token_url, headers={"Content-Type":"text", "Authorization":auth})
        if r.status_code < 300 and r.status_code > 199:
          return func(*args, **kwargs) 
        else:
          return HttpResponse('Unauthorized: no Authorization in cookies', status=401)
      else:
        return HttpResponse('Unauthorized: no code in params: ' + str(request.GET), status=401)
    else:
      return HttpResponse('Unauthorized: no request obj', status=401)

  return wrapper



