import re

import vk_api


__all__ = (
    'VkVideo',
)


class VkVideo:
    def __init__(
        self,
        vk_session: vk_api.VkApi,
        default_useragent: str = vk_api.vk_api.DEFAULT_USERAGENT,
    ) -> None:
        self._app_id = '7879029'
        self._api_version = '5.245'

        self.default_useragent = default_useragent

        self._session = vk_session
        self._session.http.headers['User-agent'] = default_useragent

    def _get_web_token(self) -> str:
        """Returns a limited-lifetime access token used by web versions of VK services."""
        data = {
            'version': self._api_version,
            'app_id': self._app_id,
        }

        access_token = self._session.storage.web_token

        if access_token is not None:
            data['access_token'] = access_token['access_token']

        resp_data = self._session.vk_login_method('web_token', data, headers={
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.vk.com',
        })

        if self._session.storage.web_token != resp_data:
            self._session.logger.info('Update web token')
            self._session.storage.web_token = resp_data
            self._session.storage.save()

        return self._session.storage.web_token['access_token']

    @staticmethod
    def parse_video_url(url: str) -> tuple[int, int]:
        """Returns the owner ID and video ID from the URL."""
        found = re.findall(r'-?\d+', url)

        if not found or len(found) != 2:
            raise ValueError('Incorrect video URL')

        owner_id, video_id = found

        return int(owner_id), int(video_id)

    def get_video_by_id(self, owner_id: int, video_id: int, access_key: str = ''):
        """
        Получить видеозапись по ID.

        Arguments:
            owner_id (in): ID владельца (отрицательные значения для групп).
            video_id (int): ID видео.
            access_key (str): Ключ доступа к объекту.
        """
        resp_data = self._session.method('video.getVideoDiscover', {
            'v': self._api_version,
            'client_id': self._app_id,
            'owner_id': owner_id,
            'video_id': video_id,
            'access_key': access_key,
            'ref': 'video',
            'updatePlaylist': 'true',
            'count': '10',
            'fields': 'screen_name,photo_50,photo_100,is_nft,verified,friend_status',
            'access_token': self._get_web_token(),
        })
        return resp_data['current_video']
