import os
import sys
import getopt
from urllib.request import urlopen
import time
from bs4 import BeautifulSoup
import youtube_dl

ydl_opts = {}
yt = "https://www.youtube.com/embed/"
nptel = "https://nptel.ac.in/courses/"


def has_class_but_no_id(tag):
    return tag.has_attr('class') and (
        'header' in tag['class']) and not tag.has_attr('id')


def get_acronym(name):
    ac = name.split()
    rv = ''
    for word in ac:
        rv += word[0]
    return rv


class Lecture:
    def __init__(self, raw_in):
        c_name = raw_in.get_text()
        onclick = raw_in['onclick']
        onclick = onclick.replace("change_video_path(", "")
        onclick = onclick.replace(")", "")
        onclick = onclick.split(",")
        self.name = c_name
        self.index = onclick[0]
        self.link = yt + (onclick[1].replace("'", ""))

    def print(self):
        print(self.index + "\t" + self.name + "\t\t" + self.link)

    def download(self):
        print("downloading " + "\t" + self.name + "\t\t" + self.link)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.link])


class Course:
    def __init__(self, course_url):
        self.course_url = course_url

    def isValidNptelcourse(self):
        return self.course_url.startswith(nptel)

    def download(self):
        response = urlopen(self.course_url).read()
        soup = BeautifulSoup(response, "html.parser")

        cwd = os.getcwd()

        ## get course title
        course_title = soup.title.get_text()
        course_title = course_title.split(":")
        course_title = course_title[len(course_title) - 1].strip()
        print(course_title)

        ## create and change to course directory
        ## can run into long path issue
        c_dir = cwd + '\\' + get_acronym(course_title)
        os.mkdir(c_dir)
        os.chdir(c_dir)

        ## parse data to get course details
        all_li = soup.find_all(has_class_but_no_id)
        for li in all_li:
            if (li.has_attr('title')):  ## is module
                ## create and change to module directory
                ## can run into long path issue
                module_name = li.get_text().strip()
                m_dir = c_dir + '\\' + get_acronym(module_name)
                os.mkdir(m_dir)
                os.chdir(m_dir)
                print(li.get_text())
            else:  ## is lecture
                lecture = Lecture(li)
                lecture.download()

    def printError(self):
        print(
            "Please enter course url in this format : https://nptel.ac.in/courses/106/102/106102064/"
        )


def main(argv):
    opts, args = getopt.getopt(argv, "")

    if (len(args) <= 0):
        print("Please enter atlease one course url")

    for arg in args:
        course = Course(arg)
        if (course.isValidNptelcourse()):
            course.download()
        else:
            course.printError()


if __name__ == "__main__":
    main(sys.argv[1:])