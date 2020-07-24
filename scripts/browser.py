import os
import shutil
from selenium import webdriver
import time

chromedriver_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../../chromedriver"
    )
)

class Browser(webdriver.Chrome):
    def __init__(self, downloads_dir):
        self.downloads_dir = downloads_dir

        options = webdriver.ChromeOptions()
        if self.downloads_dir is not None:
            options.add_experimental_option("prefs",{"download.default_directory":self.downloads_dir})
        options.gpu = False
        options.headless = False

        options.add_extension('extension.crx')

        #print(chromedriver_path)

        desired = options.to_capabilities()
        desired['loggingPrefs'] = { 'performance': 'ALL'}

        super().__init__(
            desired_capabilities=desired,
            executable_path = chromedriver_path
        )

    #def get_most_recent_download(self):
    #    #https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
    #    #print(self.downloads_dir)
    #    list_of_files = glob.glob(os.path.join(self.downloads_dir,"*"))
    #    #print(list_of_files)
    #    latest_file = max(list_of_files, key=os.path.getctime)
    #    return latest_file
    def get_local(self, path):
        self.get("file://"+ os.path.abspath(path))
    def save_mhtml(self, filename):
        wait_time = 10
        start_time = time.time()
        #https://stackoverflow.com/questions/39327032/how-to-get-the-latest-file-in-a-folder-using-python
        print("Saving from MHTML")
        files_before = os.listdir(self.downloads_dir)
        print("listed files before")
        self.execute_script("""
            var data = { type: "FROM_PAGE", text: "page.mhtml" };
            window.postMessage(data, "*");
        """)
        print("executed script")
        while True:
            files_after = os.listdir(self.downloads_dir)
            new_files = list(set(files_after).difference(set(files_before)))
            if len(new_files) > 1:
                print("Too many files!")
                time.sleep(5)
                continue
            elif len(new_files) == 1:
                most_recent_download = os.path.join(self.downloads_dir, new_files[0])
                if most_recent_download.endswith("crdownload"):
                    #Still downloading
                    continue
                else:
                    print("waiting five seconds just in case")
                    downloaded = True
                    time.sleep(5)
                    shutil.move(most_recent_download, filename)
                    break
            else:
                if time.time() - start_time > wait_time:
                    #Start over
                    return self.save_mhtml(filename)

    #def save_mhtml(self, filename):
    #    #Assume nothing else gets downloaded in the middle!
    #    self.execute_script("""
    #        var data = { type: "FROM_PAGE", text: "page.mhtml" };
    #        window.postMessage(data, "*");
    #    """)
    #    most_recent_download = os.path.join(
    #        self.downloads_dir,
    #        self.get_most_recent_download()
    #    )
    #    shutil.move(most_recent_download, filename)

#eurorad_scraper = EuroradScraper("eurorad_scraped")