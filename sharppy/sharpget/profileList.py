import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString, Node

def remove_blanks(node):
    """
    Utiltiy function to remove extra whitespace from xml file
    """
    for x in node.childNodes:
        if x.nodeType == Node.TEXT_NODE:
            if x.nodeValue:
                x.nodeValue = x.nodeValue.strip()
        elif x.nodeType == Node.ELEMENT_NODE:
            remove_blanks(x)

def createList(name, file_name):
    """
    Create new profile list xml file
    """
    root = ET.Element('profileList', name=name)
    dom = parseString(ET.tostring(root).replace('\n','')) 
    remove_blanks(dom)
    with open(file_name, 'w') as out_file:
        out_file.write(dom.toprettyxml(indent='    ').replace('\n    \n', '\n'))

class ProfileList(object):
    """
    Object representing a profile list xml document
    """
    def __init__(self, file_name):
        self.__file_name__ = file_name
        self.__root__ = ET.parse(file_name).getroot()
        self.name = self.__root__.get('name')
    def add_profile(self, model, loc, url, enabled):
        new_element = ET.Element('profile', model=model, loc=loc, url=url, enabled=('true' if enabled else 'false'))
        for x in self.__root__:
            if x.get('model') == new_element.get('model') and x.get('loc') == new_element.get('loc') and \
                x.get('url') == new_element.get('url'): 
                return
        self.__root__.append(new_element)
    def update_profile(self, index, model, loc, url, enabled):
        self.__root__[index].set('model', model)
        self.__root__[index].set('loc', loc)
        self.__root__[index].set('url', url)
        self.__root__[index].set('enabled', 'true' if enabled else 'false')
    def remove_profile(self, index):
        self.__root__.remove(self.__root__[index])
    def save(self):
        for x in self.__root__:
            x.tail = None
        self.__root__.tail = None
        dom = parseString(ET.tostring(self.__root__).replace('\n','')) 
        remove_blanks(dom)
        with open(self.__file_name__, 'w') as out_file:
            out_file.write(dom.toprettyxml(indent='    ').replace('\n    \n', '\n'))
    def __len__(self):
        return len(self.__root__)
    def __getitem__(self, index):
        return Profile(self.__root__[index])

class Profile(object):
    """
    Class representing a single profile in the profile list
    """
    def __init__(self, element):
        self.model = element.get('model')
        self.loc = element.get('loc')
        self.url = element.get('url')
        self.enabled = element.get('enabled').lower() == 'true'
    def get_archive_file(self, date):
        return '{date:s}_{model:s}_{site:s}.sharppy'.format(date=date.strftime('%Y%m%d%H'), model=self.model.lower().replace(' ', '_'), site=self.loc.lower())