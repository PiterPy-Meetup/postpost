from typing import IO, List

import requests

from api.models import PlatformPost


def get_authorization_url(client_id: int, api_version: float) -> str:
    """
    Returns a string with url for authorization.

    By following the url, you will be asked by VK to give access to the application.
    After agreement, a blank page will be displayed, and there will be an access token
    in the address bar. This token is required by functions bellow.
    """
    url = (
        'https://oauth.vk.com/authorize?client_id={client_id}&response_type=token&'
        'scope=wall,offline,groups,photos,docs&v={api_version}&'
        'redirect_uri=https://oauth.vk.com/blank.html'
    ).format(
        client_id=client_id, api_version=api_version,
    )
    return url


def send_post_to_group(
    token: str, group_id: int, api_version: float, post: PlatformPost,
) -> requests.Response:
    """
    Sends post to vk group on behalf of the group itself.
    """
    vk_api = VkAPI(token, api_version)
    attachments = []
    # TODO: Add attachments uploading according to PlatformPost changes
    return vk_api.send_post_to_group_wall(group_id, post.text_for_posting, attachments)


class VkAPIError(Exception):
    """
    Vk API base exception.
    """

    def __init__(self, method: str, payload: dict, response: bytes):
        """
        Init error.
        """
        message = '{0} {1} {2}'.format(method, payload, response)
        super(VkAPIError, self).__init__(message)


class VkAPI(object):
    """
    Local mini client for vk API.

    Its purpose is to share token, api version, and error handling among the api methods.
    """

    def __init__(self, token: str, api_version: float):
        """
        Init client.
        """
        self._token = token
        self._api_version = api_version
        self._url = 'https://api.vk.com/method/'

    def send_post_to_group_wall(self, group_id: int, message: str, attachments: List[str] = None):
        """
        Sends post to vk group on behalf of the group itself.
        """
        payload = {
            'owner_id': -group_id,
            'from_group': 1,
            'message': message,
        }
        if attachments:
            payload['attachment'] = ','.join(attachments)
        response = self._request('wall.post', payload=payload)
        return response

    def upload_doc(self, doc: IO) -> str:
        """
        Uploads and saves doc on the server.
        """
        upload_url = self._request('docs.getWallUploadServer')['upload_url']

        response = requests.post(upload_url, files={'file': doc})
        if response.status_code != requests.codes.ok or 'error' in response.json():
            raise VkAPIError(upload_url, {'file': doc}, response.content)

        doc = self._request(
            'docs.save',
            {'file': response.json()['file']},
        )['doc']
        return 'doc{0}_{1}'.format(doc['owner_id'], doc['id'])

    def upload_photo(self, group_id: int, photo: IO) -> str:
        """
        Uploads and saves photo in the community wall photos.
        """
        upload_url = self._request(
            'photos.getWallUploadServer',
            {'group_id': group_id},
        )['upload_url']

        response = requests.post(upload_url, files={'file': photo})
        if response.status_code != requests.codes.ok or 'error' in response.json():
            raise VkAPIError(upload_url, {'file': photo}, response.content)
        uploaded_photo = response.json()

        photo = self._request('photos.saveWallPhoto', {
            'group_id': group_id,
            'server': uploaded_photo['server'],
            'hash': uploaded_photo['hash'],
            'photo': uploaded_photo['photo'],
        })[0]
        return 'photo{0}_{1}'.format(photo['owner_id'], photo['id'])

    def _request(self, method: str, payload: dict = None):
        if payload is None:
            payload = {}
        payload.update({
            'v': self._api_version,
            'access_token': self._token,
        })
        response = requests.post(self._url + method, data=payload)
        if response.status_code != requests.codes.ok or 'error' in response.json():
            raise VkAPIError(method, payload, response.content)
        return response.json()['response']