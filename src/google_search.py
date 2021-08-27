import requests, json
from re import findall as re_match
from bs4 import BeautifulSoup
from uuid import uuid4
from urllib.parse import urlparse

class Google:
    google_urls = {
        "webcache.googleusercontent.com",
    }

    search_content = {
        "title",
        "content",
        "url",
    }

    def __init__(self, to_hide = []):
        self.search_content = [not (val in to_hide) and val for val in self.search_content]

class GoogleSearch(Google):
    def __init__(self, to_hide=[]):
        super().__init__(to_hide=to_hide)

    def format_search_data(self, raw_content):
        response_data = []
        bs = BeautifulSoup(raw_content, "html.parser")
        results = [bs.find_all("div", {"class": classname}) for classname in ["g", "ULSxyf", "hlcw0c"]]

        raw_decoded = raw_content.decode("utf-8", errors='ignore')

        for c in results:
            for result in c:

                individual_data = {}

                if "title" in self.search_content:
                    individual_data.update({"title": data.text for data in result.find_all("div", {"role": "heading"})})

                if "url" in self.search_content:
                    for link in [data.get("href") for data in result.find_all("a")]:
                        for banned in self.google_urls:
                            if not banned in link and "https://" in link:
                                individual_data.update({"url": link})
                
                if "content" in self.search_content:
                    individual_data.update({"content": data.text for data in result.find_all("div", {"class": "VwiC3b MUxGbd yDYNvb lyLwlc"})})

                #individual_data.update({"count": bs.find_all("div", {"id": "result-stats"})[0].text})

                response_data.append(individual_data)

        return response_data

    def search(self, search_query: str, exact_match: bool = False, num: int = 100, log: bool = False):
        params = {
                "q": urlparse(exact_match and f"\"{search_query}\"" or search_query).geturl(),
                "num": str(num),
        }

        SEARCH_REQ = requests.get("https://www.google.com/search", params = params, headers = {
                "User-Agent": "Firefox",
                "Cookie": "NID=222=qmL2ueMBsCu1FZnlSe-_s5sPO8gewpuPe95BNduCOwNh7lNUwbAAvP86LSWtCJVC05_Mde2d5pHs8vgYbnddYHCPVMKr5kQ_2Pcpgd7hVJzk6jfMfvtaQ33hcy6jDefcJ32ZuDSCo5diIijaznUiJlUlnNgIPKnd0bwLoYvujg5xqrKyrqYheItaVf0GvtHL1zMvmWSRzKcdHuQeHPoFxglh;",
            }
        )

        if SEARCH_REQ.status_code != 200:
            return False, f"Bad response: {SEARCH_REQ.status_code}"

        search_results = self.format_search_data(SEARCH_REQ.content)

        if log:
            with open(f"../logs/{search_query}_{str(uuid4())[:5]}.json", "w") as log_file:
                json.dump(search_results, log_file, sort_keys=True, indent=4)

        return SEARCH_REQ.status_code, search_results
