class Option:
    # options dictionary is of form:
    #   __options = {'name': [default,current_value,callback]}
    __options = None
    def __init_options(self,options=()):
        # options is a list of tuples of the form:
        #   (name, default_value, callback)
        # callback function can be either a string, which will be called
        #   as an instance-level function, i.e.:
        #      eval("self."+callback)()
        #   or can be a function, which will be called directly, i.e.:
        #      callback()
        if self.__options is None:
            self.__options = {}
        for option_tup in options:
            assert len(option_tup)>=2, ('Must be of form: '
                                        '(name,default[,callback])')
            name = option_tup[0]
            default = option_tup[1]
            func=None
            if len(option_tup)>2:
                func = option_tup[2]
            if name in self.__options:
                self.__options[name][0] = default
                self.__options[name][1] = default
                if func:
                    self.__options[name][2] = func
            else:
                self.__options[name]=[default,default,func]
    def __getitem__(self,key):
        return self.GetOption(key)
    def __setitem__(self,key,value):
        self.SetOption(key,value)
    def HasOption(self,key):
        if key in self.__options:
            return True
        return False
    def GetOption(self,key=None):
        self.__init_options()
        self_options = self.__options
        if key is None:
            options = {}
            for name,tup in self_options.items():
                options[name]=str(tup[1])
            return options
        value = self_options[key][0]
        if hasattr(self,'return_option_%s'%key):
            value = eval('self.return_option_%s()'%key)
        return value
    def SetOption(self,key,value,call=True,check=True):
        self.__init_options()
        if check:
            errstr = (key+' is not a valid option for '+
                      self.__class__.__name__)
            assert key in self.__options,errstr
        else:
            if not key in self.__options:
                # XXX do this?
                return
                self.__options[key]=[None,value,None]
        self.__options[key][0]=value
        if call:
            func = self.__options[key][2]
            if func:
                func()
    def InitOptions(self,options,kw,required_options=[]):
        need_options = []
        for option in required_options:
            if option not in kw:
                need_options.append(options)
        if need_options:
            s = 'Option(s) %s not provided. Must provide at instantiation.'%need_options
            raise AttributeError, s
        self.__init_options(options)
        for key,value in kw.items():
            self.SetOption(key,value,False,False)
        
