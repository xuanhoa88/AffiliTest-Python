import requests
from urllib import parse
from affilitest import endpoints
import copy

class AffiliTest(object):
  def __init__(self, api_key=None):
    self.api_key = api_key


  def login(self, email, password):
    return self._post(endpoints.LOGIN, {'email' : email, 'password' : password})

  def logout(self):
    return self._get(endpoints.LOGOUT)

  def app_info(self, url = None, package = None, country = None):
    if url is None and package is None:
      raise APIException('No parameters were passed to appInfo', endpoints.APPINFO)
    if url is not None and package is not None:
      raise APIException('Only one parameter should be passed', endpoints.APPINFO)
    if url is not None:
      return self._app_info_fetch(url, 'url')
    return self._app_info_fetch(package, 'package', country)

  def _app_info_fetch(self, data, type, country = None):
    payload = {type : data}
    if country:
      payload['country'] = country
    return self._get(endpoints.APPINFO, payload)

  def test(self, url, country, device):
    return self._post(endpoints.TEST, {
      'url' : url,
      'country' : country,
      'device' : device
    })

  def clone(self):
    api_clone = copy.deepcopy(self)
    api_clone._request_session = requests.Session()
    api_clone._request_session.cookies = self._request_session.cookies
    return api_clone

  def compare_to_preview(self, url, preview_url, country, device):
    return self._post(endpoints.TEST, {
      'url' : url,
      'previewURL' : preview_url,
      'country' : country,
      'device' : device
    })

  def _post(self, endpoint, payload):
    self._last_response = self.requests_session().post(endpoint, data = payload, headers = {'Authorization': 'AT-API ' + self.api_key})
    try:
      resData = self._last_response.json()
    except Exception as e:
      raise APIException('API response error. Status code {} '.format(self._last_response.status_code), endpoint)
    if resData['error']:
      raise APIException(resData['error'], endpoint)
    return resData['data']

  def _get(self, endpoint, payload = None):
    url = endpoint
    if payload is not None:
      url = endpoint + '?' + parse.urlencode(payload)
    self._last_response = self.requests_session().get(url, headers = {'Authorization': self.api_key})
    resData = self._last_response.json()
    if resData['error']:
      raise APIException(resData['error'], endpoint)
    return resData['data']

  def last_response(self):
    return self._last_response

  def requests_session(self):
    if hasattr(self, '_request_session'):
      return self._request_session
    self._request_session = requests.Session()
    return self._request_session


class APIException(Exception):
  def __init__(self, error, endpoint):
    super(APIException, self).__init__(error, endpoint)
    self.endpoint = endpoint