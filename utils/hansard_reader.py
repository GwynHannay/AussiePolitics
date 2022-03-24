import xml.etree.ElementTree as et

tree = et.parse('hansard/Senate_2022_02_10_Official.xml')
root = tree.getroot()

def read_senate():
    for child in root:
        if child.tag == 'session.header':
            for session in child:
                print(session.tag, session.text)

        # print("First:", child.tag)
        # for info in child:
        #     print("Then:", info.tag, info.text)

        #     if info.tag == 'business.start':
        #         for business in info:
        #             print("Bus:", business.tag, business.attrib)