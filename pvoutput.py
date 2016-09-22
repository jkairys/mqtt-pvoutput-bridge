import requests, datetime
_api_key = None
_system_id = None
_url = "http://pvoutput.org/service/r2/addstatus.jsp"

# minimum seconds between uploads
_min_upload_interval = 5*60
_buffer = []
_last_sent = None

def upload(watts, temperature, voltage):
  if(last_sent is not None and datetime.datetime.now() < _last_sent + datetime.timedelta(seconds=_min_upload_interval)):
    _buffer.append({"watts": watts, "temperature": temperature, "voltage": voltage})
  else:
    # calculate the average of these quantities
    avg = {"watts": 0, "temperature": 0, "voltage": 0}
    for qty in avg.keys():
      for m in _buffer:
        avg[qty] = avg[qty] + m[qty]
      avg[qty] = round(avg[qty] / len(_buffer[qty]),1)

    last_sent = datetime.datetime.now()
    _send(avg["watts"], avg["temperature"], avg["voltage"])
    _buffer = []

def send(watts, temperature=None, voltage=None):

  if(_api_key is None or _system_id is None):
    raise ValueError("You must specify an API Key and System ID")
  headers = {
    "X-Pvoutput-Apikey": _api_key,
    "X-Pvoutput-SystemId": _system_id
  }
  data = {
    "d": datetime.datetime.now().strftime("%Y%m%d"),
    "t": datetime.datetime.now().strftime("%H:%M"),
    "v2": watts,
    "v5": temperature,
    "v6": voltage
  }
  #print(data)
  result = requests.post(_url, data, headers=headers)
  #print(result.text)
  _last_sent = datetime.datetime.now()
