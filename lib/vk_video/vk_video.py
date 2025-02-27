import typing as t
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

    def _select_best_quality(
        self,
        files: t.Dict[str, str],
        quality: int = -1,
        preferred_order: t.Tuple[str, ...] = (
            'dash_ondemand', 'hls_ondemand', 'hls', 'dash_sep', 'dash_webm', 'mp4', 'failover_host',
        ),
    ) -> t.Tuple[str, str]:
        """Returns the format name and URL to the video in the best quality."""
        for fmt in preferred_order:
            if fmt in files:
                return fmt, files[fmt]

            if fmt == 'mp4':
                quality_list = sorted(
                    (i for i in files.keys() if i.startswith('mp4_')),
                    key=lambda x: int(x.split('_')[1]),
                    reverse=True,
                )

                if quality < 0:
                    fmt = quality_list[0]
                    return fmt, files[fmt]

                quality = max(144, quality)

                for i in quality_list:
                    if int(i.split('_')[1]) <= quality:
                        return i, files[i]

        raise ValueError('Unknown video format or quality.')

    @staticmethod
    def parse_video_url(url: str) -> tuple[int, int]:
        """Returns the owner ID and video ID from the URL."""
        found = re.findall(r'-?\d+', url)

        if not found or len(found) != 2:
            raise ValueError('Incorrect video URL')

        owner_id, video_id = (int(i) for i in found)

        return owner_id, video_id

    def get_video_by_id(
        self,
        owner_id: int,
        video_id: int,
        access_key: str = '',
        quality: int = -1,
    ):
        """
        Get video with specified quality.

        Arguments:
            owner_id (in): Owner ID (negative values for groups).
            video_id (int): Video ID.
            access_key (str): Access key to the object.
            quality (int): Video quality. A value of -1 will return the maximum.
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
        video = resp_data['current_video']
        video['best_fmt'], video['best_url'] = self._select_best_quality(video['files'], quality=quality)
        return video
