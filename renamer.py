import os
import json
import re


def renamer(folder_path, add_key_words):
    main_folder_path = folder_path
    json_file_path = "renamer.json"
    array = add_key_words

    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
        links = data.get("links", [])
        titles = data.get("titles", [])

    for folder_name in os.listdir(main_folder_path):
        folder_path = os.path.join(main_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for video_name in os.listdir(folder_path):
                video_code = extract_video_code(video_name)
                if video_code:
                    matching_title = find_matching_title(video_code, titles)
                    if matching_title:
                        new_video_name = sanitize_filename(
                            rename_video(video_name, matching_title, array)
                        )
                        original_path = os.path.join(folder_path, video_name)
                        new_path = os.path.join(folder_path, (new_video_name))
                        os.rename(original_path, new_path)
                        print(f"Renamed: '{video_name}' to '{new_video_name}'")
                        try:
                            os.rename(
                                folder_path,
                                os.path.join(
                                    main_folder_path,
                                    os.path.splitext(new_video_name)[0],
                                ),
                            )
                        except:
                            os.rename(
                                folder_path,
                                os.path.join(
                                    main_folder_path,
                                    f"{os.path.splitext(new_video_name)[0]} ({os.path.basename(folder_path)})",
                                ),
                            )


def extract_video_code(video_name):
    # Use regular expression to extract the video code from the name
    pattern = r"[A-Za-z]+-\d+"
    match = re.search(pattern, video_name)
    if match:
        return match.group(0)
    return None


def find_matching_title(video_code, titles):
    for title in titles:
        if video_code.lower() in title.lower():
            return title
    return None


def rename_video(video_name, matching_title, array):
    # Remove file extension from the video name
    name_without_extension, extension = os.path.splitext(video_name)
    # Create the new name with the matching title and the array words
    if(len(array) != 0):
        new_name = f"{matching_title} ({', '.join(array)}){extension}"
    return new_name


def sanitize_filename(filename):
    # Replace illegal characters with underscores
    illegal_chars = '<>:"/\\|?*'
    for char in illegal_chars:
        filename = filename.replace(char, "_")
    return filename


if __name__ == "__main__":
    videoDirectory = "./video-folder"

    #additional keywords you want added to your file names
    #like:
    #from original video file name: eg:"abc-123 blah blah"
    #with the array ["you","are a","discord mod"]
    #to new file name "abc-123 blah blah (you, are a, discord mod)"
    #leave empty if you don't want to use this
    #keep in mind this will not rename the file with the additional keywords if it doesn't find a match for the code in video-folder
    addkeywords = [
        "key1",
        "key2",
        "key3"
    ]

    renamer(
        videoDirectory,
        addkeywords,
    )
