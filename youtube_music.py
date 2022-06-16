import ytmusicapi


class music:
    def __init__(self):
        self.ytmusic = ytmusicapi.YTMusic()

    def get_search_result(self, req):
        result = self.ytmusic.search(req)
        answer = [(item.get('title'), item.get('duration'), item.get('videoId')) for item in result
                  if item.get('resultType') == 'song' or item.get('resultType') == 'video']

        return answer

    def get_video_link(self, item_from_yt_result):
        return f'https://www.youtube.com/watch?v={item_from_yt_result.split()[-1]}'


if __name__ == "__main__":
    music = music()
    print(music.get_search_result("рамамба хара"))
