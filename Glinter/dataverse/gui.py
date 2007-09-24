from Tkinter import *
import Pmw
from learn import *

class DataverseGUI(Frame):
    def __init__(self,parent=None,*a,**kw):
        Frame.__init__(self,parent,*a,**kw)
        self.configure({'bg':'tan'})

        ts = self.topsection = Pmw.Group(self,tag_pyclass=None)
        #ts.pack(side='top',fill='both',expand='yes',anchor='s')
        ts.grid()#sticky="news")
        tsf = ts.interior()

        self.status = Pmw.MessageBar(self,labelpos='w',label_text='Status:')
        #self.status.pack(side='bottom',fill='x',expand=1,anchor='s')
        self.status.grid(row=1,sticky="ew")

        self.map = Pmw.ScrolledCanvas(tsf,
                                      canvas_bg="white",
                                      canvas_width=500,
                                      canvas_height=400)
        #self.map.pack(side='right',expand=1,fill='both')
        self.map.grid(row=0,column=1,sticky="news")

        lb = self.leftbar = Pmw.Group(tsf,
                                      tag_text='Left Group')
        #lb.pack(side='left',fill='y',expand='yes',anchor='w')
        lb.grid(row=0,column=0,sticky="ns")

        lbf = lb.interior()

        self.current_topic_var = ctv = StringVar()
        ct = self.current_topic = Label(lbf,textvariable=ctv,
                                        )
        ct.grid()
        
        te = self.topic_entry = Pmw.EntryField(lbf,
                                      labelpos='w',label_text='Topic:',
                                      command=self.TopicCommand,
                                      )
        te.component('entry').focus_set()
        #te.pack(side='top')#,expand=1,fill='y')
        te.grid()

        qe = self.qual_entry = Pmw.ScrolledText(lbf,
                                              labelpos='n',
                                              label_text='Quality',
                                              text_width=30,
                                              text_height=5,
                                              )
        qe.component('text').bind('<Control-KeyPress-backslash>',
                                  self.NewQuality)
        #qe.pack(side='top',expand=1,fill='y')
        qe.grid(sticky="ns")

        ql = self.qual_list = Pmw.ScrolledListBox(lbf,
                                                labelpos='n',
                                                label_text='Quality List',
                                                )
        #ql.pack(side='top',expand=1,fill='y')
        ql.grid(sticky="ns")

        self.pack(fill='both',expand=1)
        #self.grid(row=0,sticky='news')

        self._root().bind('<Control-q>',lambda e,s=sys:s.exit(0))


    current_topic_id = None
    dataverse = Dataverse()
    def TopicExists(self,object):
        return self.dataverse.TopicExists(object)
    def SetCurrentTopic(self,tid):
        text = self.dataverse.GetTopicTitle(tid)
        self.current_topic_id = tid
        self.current_topic_var.set('Current topic: %s'%text)
        self.Refresh()
    def TopicCommand(self):
        text = self.topic_entry.get().strip()
        tid = self.TopicExists(text)
        if not tid:
            self.NewTopic(text)
        else:
            self.SetCurrentTopic(tid)
    def NewTopic(self,text):
        tid = self.dataverse.AddTopic(text)
        self.SetCurrentTopic(tid)
        print 'Topic added:',tid
        
    def NewQuality(self,*a):
        #print a[0].keycode,a[0].keysym
        curtid = self.current_topic_id
        if curtid:
            text = self.qual_entry.get().strip()
            qid = self.dataverse.AddQuality(curtid,text)
            print 'Quality added:', qid
        self.Refresh()

    def Refresh(self):
        self.refresh_topic_entry()
        self.refresh_qual_entry()
        self.refresh_qual_list()
    def refresh_topic_entry(self):
        self.topic_entry.clear()
    def refresh_qual_entry(self):
        self.qual_entry.clear()
        self.qual_entry.component('text').focus_set()
    def refresh_qual_list(self):
        curtid = self.current_topic_id
        qualities = self.dataverse.GetQualities(curtid)
        strlist = []
        for quality in qualities:
            strlist.append(str(quality))
        self.qual_list.setlist(strlist)

    def refresh_map(self):
        pass
        
        

if __name__=='__main__':
    w = DataverseGUI()
    w.mainloop()
