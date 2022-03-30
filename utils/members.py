import xml.etree.ElementTree as et

def get_people():
    tree = et.parse('hansard/people.xml')
    root = tree.getroot()

    for person in root:
        print(person.attrib['latestname'])