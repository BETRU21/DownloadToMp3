import youtube_dl

class Download2Mp3:
    def __init__(self, view=False):
        self.notDownloaded = []
        self.setupDownloadParam()

    # Public functions

    def downloadMusicFile(self, url):
        if type(url) is not str:
            raise TypeError("url argument is not a string.")
        try:
            with youtube_dl.YoutubeDL(self.ydlParams) as ydl:
                ydl.download([url])
        except Exception as e:
            e = str(e)
            self.notDownloaded.append(url)
            raise RuntimeError("Something went wrong.")

    def musicsNotDownloaded(self):
        return self.notDownloaded

    # Non-Public functions

    def callableHook(self, response):
        if view == True:
            if response["status"] == "downloading":
                dlPercent = round((response["downloaded_bytes"]*100)/response["total_bytes"],1)
                eta = response["eta"]
                downloadPercent = f"{dlPercent}%"
                estimatedTime = f"{eta}s"

                self.view.downloadStatus(downloadPercent, estimatedTime)
        else:
            pass

    def setupDownloadParam(self):
        self.ydlParams = {
        "progress_hooks": [self.callableHook],
        'outtmpl': 'downloadMusics/%(title)s.%(ext)s',
        'noplaylist': True,
        'format': 'bestaudio/best',
        'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',}],}
