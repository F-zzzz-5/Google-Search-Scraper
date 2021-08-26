from google_search import GoogleSearch

if __name__ == "__main__":
    
    google = GoogleSearch()
    success, results = google.search(input("Search: "), exact_match=True, num=20, log=True)
    
    print(success)

    if success and results:
        for result in results:
            for key, value in result.items():
                pass
                #print(key, value)
