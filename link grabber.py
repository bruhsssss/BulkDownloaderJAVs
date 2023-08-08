import sys
import requests
from bs4 import BeautifulSoup
import json
from tqdm import tqdm
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QCheckBox, QPushButton, QTextBrowser, QMessageBox, QProgressBar
)
from PyQt5 import QtCore  # Import the QtCore module

result_dict = {
    "titles": [],
    "links": []
}

def get_video_links_and_titles(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    video_links_and_titles = []

    for div in soup.find_all("div", class_="video"):
        link = div.find("a", class_="thumbnail")["href"]
        title = div.find("span", class_="video-title").text.strip()
        video_links_and_titles.append(("https://javhd.today"+link, title))

    return video_links_and_titles

def main(url,numPages,unwanted_words,deep_search,ui):
    base_url = url
    num_pages = numPages

    video_links_and_titles = []
    for page in range(1, num_pages + 1):
        page_url = f"{base_url}&page={page}"
        video_links_and_titles += get_video_links_and_titles(page_url)
    if not video_links_and_titles:
        QMessageBox.information(ui, "Result","No videos found")
        return {
            "titles": [],
            "links": []
        }
    unfiltered = len(video_links_and_titles)
    video_links_and_titles = [f for f in video_links_and_titles if not any(word in f[0] for word in unwanted_words) and not any(word in f[1] for word in unwanted_words)]
    filtered_video_links_and_titles = []
    for index, (link, title) in enumerate(tqdm(video_links_and_titles, desc="Processing links",unit="link")):
        if not any(word in title.lower() for word in unwanted_words) and (deep_search):
            progress_percentage = (index / len(video_links_and_titles)) * 100
            ui.progress_bar.setValue(int(progress_percentage))
            response = requests.get(link)
            soup = BeautifulSoup(response.text, "html.parser")
            tags = soup.find_all("i", class_="fa fa-tag")
            tag_phrases = [tag.find_parent("a").text.strip() for tag in tags]
            if any(any(word in phrase.lower() for word in unwanted_words) for phrase in tag_phrases):
                continue
            filtered_video_links_and_titles.append((link, title))
            # Update the progress bar based on the current index
        elif not deep_search:
            filtered_video_links_and_titles = video_links_and_titles
    ui.progress_bar.setValue(int(100))


    if not filtered_video_links_and_titles:
        QMessageBox.information(ui, "Result", "No videos found after filtering.")
        return {
            "titles": [],
            "links": []
        }
    
    QMessageBox.information(ui, "Result", f"Video(s) found without filtering:{unfiltered}\nVideo(s) found after filtering:{len(filtered_video_links_and_titles)}")
    for link, title in filtered_video_links_and_titles:
        result_dict["titles"].append(title)
        result_dict["links"].append(link)
    return result_dict


class VideoLinkExtractorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Link Extractor")
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout(main_widget)
        
        header_labels = [
            "The URL",
            "The number of pages you want to extract",
            "Add your list of unwanted words here, this will filter out all the video names with any of the words/phrases inside the array",
            "Set this to True if you also want this program to check the tags of the video keep in mind it takes a bit longer if it checks the tags (because it opens all the links and gets the tags out of the webpage)"
        ]

        input_layout = QVBoxLayout()
        for label_text in header_labels:
            label = QLabel(label_text)
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            input_layout.addWidget(label)
        
        self.url_entry = QLineEdit(self)
        self.url_entry.setPlaceholderText("Enter URL")
        input_layout.addWidget(self.url_entry)
        
        self.num_pages_entry = QLineEdit(self)
        self.num_pages_entry.setPlaceholderText("The number of pages you want to extract")
        input_layout.addWidget(self.num_pages_entry)

        self.unwanted_entry = QTextEdit(self)
        self.unwanted_entry.setPlaceholderText("Unwanted Words/Phrases (one per line) \nAdd your list of unwanted words here, this will filter out all the video names with any of the words/phrases inside the array")
        input_layout.addWidget(self.unwanted_entry)
        
        self.deep_search_checkbox = QCheckBox("Perform Deep Search(Filter the videos using tags)", self)
        self.deep_search_checkbox.setToolTip("Set this to True if you also want this program to check the tags of the video, keep in mind it takes a bit longer if it checks the tags (because it opens all the links and gets the tags out of the webpage)")
        input_layout.addWidget(self.deep_search_checkbox)

        button_layout = QHBoxLayout()
        self.extract_button = QPushButton("Extract Links", self)
        self.copy_button = QPushButton("Copy Links to Clipboard", self)
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.copy_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMaximum(100)  # Set the maximum value for the progress bar
        input_layout.addWidget(self.progress_bar)

        self.links_browser = QTextBrowser(self)

        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.links_browser)

        self.extract_button.clicked.connect(self.run_extraction)
        self.copy_button.clicked.connect(self.copy_to_clipboard)

    def run_extraction(self):
        with open("renamer.json", 'w') as json_file:
            json.dump(result_dict, json_file)

        with open("links.txt", 'w') as txt_file:
            txt_file.write("")

        # Clear result_dict
        result_dict["titles"] = []
        result_dict["links"] = []
        self.links_browser.clear()

        url = self.url_entry.text()
        numPages = int(self.num_pages_entry.text())
        unwanted = self.unwanted_entry.toPlainText().splitlines()
        deep_search = self.deep_search_checkbox.isChecked()

        try:
            jsondumper = main(url, numPages, unwanted, deep_search,self)
            if(len(jsondumper["titles"]) != 0):
                links_text = ""
                for link in jsondumper["links"]:
                    links_text += link + "\n"
                self.links_browser.setPlainText(links_text)

                with open("renamer.json", 'w') as json_file:
                    json.dump(jsondumper, json_file)

                with open("links.txt", 'w') as txt_file:
                    for link in jsondumper["links"]:
                        txt_file.write(link + "\n")

                QMessageBox.information(self, "Extraction Complete", "Extraction and saving results are complete.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.links_browser.toPlainText())
        QMessageBox.information(self, "Copy to Clipboard", "Links copied to clipboard.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = VideoLinkExtractorApp()
    mainWin.show()
    sys.exit(app.exec_())
