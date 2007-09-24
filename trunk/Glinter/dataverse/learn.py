import os,sys,time,pickle
import elementtree.ElementTree as etree
import xml.dom.minidom as mini
import xml.dom.ext as ext

class Object:
    def __init__(self,**kw):
        self.attrib = {'id':id(self),
                       'creation': time.asctime(),
                       }
        self.attrib.update(kw)
        self.text = None
    def __getitem__(self,key):
        return self.attrib[key]
    def __setitem__(self,key,value):
        self.attrib[key]=value
    def attrib_toxml(self):
        attrib={}
        for key,value in self.attrib.items():
            attrib[key]=str(value)
        return attrib
    def toxml(self):
        e = etree.Element(self.__class__.__name__,**self.attrib_toxml())
        e.text = self.text
        return e
    def GetText(self):
        return self.text
    def fromxml(self,element):
        self.attrib.update(element.attrib)
        self.text = element.text

class Topic(Object):
    def __init__(self,title='',**kw):
        Object.__init__(self,**kw)
        self.attrib['title'] = title
        self.qualities = []
    def GetTitle(self):
        return self.attrib['title']
    def SetTitle(self,title):
        self.attrib['title']=title
    def AddQuality(self,text):
        q = Quality(text)
        self.qualities.append(q)
        return q['id']
    def GetQualities(self):
        qualities = []
        for q in self.qualities:
            qualities.append(q.GetText())
        return qualities
    def toxml(self):
        e = etree.Element('Topic',**self.attrib_toxml())
        for q in self.qualities:
            qe = q.toxml()
            e.append(qe)
        return e
    def fromxml(self,element):
        self.attrib.update(element.attrib)
        for qe in element.getchildren:
            q = Quality()
            q.fromxml(element)

class Quality(Object):
    def __init__(self,text=None,**kw):
        Object.__init__(self,**kw)
        self.text=text

class Link(Object):
    def __init__(self,topics=[],**kw):
        Object.__init__(self,**kw)
        self.topics = []
        self.append(topics)
    def append(self,object):
        if type(object) in (type(()),type([])):
            self.topics.extend(object)
        else:
            self.topics.append(object)
    def GetQualities(self,topic):
        qualities = []
        for topic in self.topics:
            qualities.extend(topic.GetQualities())
        return qualities
    def toxml(self):
        e = etree.Element('Link',**self.attrib_toxml())
        for t in self.topics:
            te = etree.Element('TopicID',id=t['id'])
            e.append(te)
        return e

from types import *

class Dataverse(Object):
    index=1
    def __init__(self):
        Object.__init__(self)
        self.objects = {'Topic':[],
                        'Link':[],
                        }
    def add_object(self,object):
        # internal, for use with AddObject and fromxml functions
        otype = object.__class__.__name__
        self.objects[otype].append(object)
    def AddObject(self,object):
        object['id'] = self.index
        self.index += 1
        self.add_object(object)
    def GetTopics(self):
        return self.objects['Topic']
    def GetTopic(self,tid):
        for t in self.GetTopics():
            if t['id'] == tid:
                return t
        raise AttributeError, "No topic with that id: %s"%tid
    def TopicExists(self,object):
        topics = self.GetTopics()
        if type(object) is StringType: #title
            for topic in topics:
                if object.lower() == topic.GetTitle().lower():
                    return topic['id']
            return 0
        elif type(object) is IntType: #topic id
            for t in topics:
                if t['id'] == object:
                    return 1
            return 0
        else:
            raise SyntaxError, "You shouldn't have a Topic object..."
        
    def GetTopicTitle(self,tid):
        return self.GetTopic(tid).GetTitle()
    def SetTopicTitle(self,tid,text):
        t = self.GetTopic(tid)
        t.SetTitle(text)
    def AddTopic(self,text):
        topic = Topic(text)
        self.AddObject(topic)
        return topic['id']

    def AddQuality(self,tid,text):
        t = self.GetTopic(tid)
        return t.AddQuality(text)
    def GetQualities(self,tid):
        return self.GetTopic(tid).GetQualities()

    def GetLinks(self):
        return self.objects['Link']
    def AddLink(self,topics):
        link = Link(topics)
        self.AddObject(link)
        return link['id']

    def toxml(self,file=None):
        e = etree.Element('Dataverse',**self.attrib_toxml())
        for t in self.GetTopics():
            te = t.toxml()
            e.append(te)
        for l in self.GetLinks():
            le = l.toxml()
            e.append(le)
        s = etree.tostring(e)
        doc = mini.parseString(s)
        ext.PrettyPrint(doc)
