import youtube_dl

class Download2Mp3:
    def __init__(self, CallableHook=None):
        self.hook = CallableHook
        self.notDownloaded = []
        self.setupDownloadParam()

    # Public functions
    def getPlaylistUrl(self, url):
        ydlPlaylist = youtube_dl.YoutubeDL({'dump_single_json': True, 'extract_flat' : True})
        with ydlPlaylist:
            result = ydlPlaylist.extract_info(url, False)
        listSong = []
        try:
            numberSong = len(result.get("entries"))
        except:
            raise ValueError("This playlist is not valid for this action")
        for i in range(numberSong):
            ids = result.get("entries")[i].get("id")
            listSong.append(f"https://www.youtube.com/watch?v={ids}")
        return listSong


    def downloadMusicFile(self, url):
        if type(url) is not str:
            raise TypeError("url argument is not a string.")
        try:
            with youtube_dl.YoutubeDL(self.ydlParams) as ydl:
                ydl.download([url])
        except Exception as e:
            e = str(e)
            self.notDownloaded.append(url)
            raise RuntimeError(e)

    def musicsNotDownloaded(self):
        return self.notDownloaded

    # Non-Public functions

    def setupDownloadParam(self):
        if self.hook == None:
            self.ydlParams = {
            'outtmpl': 'downloadMusics/%(title)s.%(ext)s',
            'noplaylist': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',}],}
        else:
            self.ydlParams = {
            "progress_hooks": [self.hook],
            'outtmpl': 'downloadMusics/%(title)s.%(ext)s',
            'noplaylist': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',}],}
