import os
from exercise_02 import write_list_to_file


def foldersToFile(path):
    folder_list = []
    for _, folders, _ in os.walk(path):
        for name in folders:
            folder_list.append(name)
    write_list_to_file(
        '/home/jovyan/my_notebooks/my_data/exercise02/foldersList.txt', folder_list)


def filesAndFoldersRecursively(path):
    file_list = []
    for _, _, files in os.walk(path):
        for file in files:
            file_list.append(file)
    write_list_to_file(
        '/home/jovyan/my_notebooks/my_data/exercise02/filesList.txt', file_list)


def readFirstLineOfFiles(filePaths):
    for filePath in filePaths:
        with open(filePath) as file_object:
            print(file_object.readline())


def findEmailsInFiles(filePaths):
    for filePath in filePaths:
        with open(filePath) as file:
            lines = file.readlines()
            for line in lines:
                if '@' in line:
                    print(line)


def headlinesFromMDFiles(filePaths):
    for filePath in filePaths:
        with open(filePath) as file:
            for line in file.readlines():
                if line[0] == '#':
                    print(line)


if __name__ == "__main__":
    headlinesFromMDFiles(
        ['/home/jovyan/my_notebooks/my_data/exercise02/markdown.md'])
    foldersToFile('/home/jovyan/my_notebooks/my_modules')
