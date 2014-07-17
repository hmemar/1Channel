from addon.common.addon import Addon

_1CH = Addon('plugin.video.1channel')
class PW_Dispatcher:
    def __init__(self):
        self.func_registry={}
        self.args_registry={}
        self.kwargs_registry={}

    def register(self, mode, args=None, kwargs=None):
        """
        Decorator function to register a function as a plugin:// url endpoint
        
        mode: the mode value passed in the plugin:// url
        args: a list  of strings that are the positional arguments to expect
        kwargs: a list of strings that are the keyword arguments to expect 
        
        * Positional argument must be in the order the function expect
        * kwargs can be in any order
        * kwargs without positional arguments are supported by passing in a kwargs but no args
        * If there are no arguments at all, just "mode" can be specified
        """
        if args is None:
            args=[]
        if kwargs is None:
            kwargs=[]
                
        def decorator(f):
            if mode in self.func_registry:
                message='Error: %s already registered as %s' % (str(f), mode)
                _1CH.log_error(message)
                raise Exception(message)

            _1CH.log_debug('registering function: |%s|->|%s|' % (mode,str(f)))
            self.func_registry[mode.strip()]=f
            self.args_registry[mode]=args
            self.kwargs_registry[mode]=kwargs
            _1CH.log_debug('registering args: |%s|-->(%s) and {%s}' % (mode, args, kwargs)) 
            
            return f
        return decorator

    def dispatch(self, mode, queries):
        """
        Dispatch function to execute function registered for the provided mode
        
        mode: the string that the function was associated with
        queries: a dictionary of the parameters to be passed to the called function
        """
        if mode not in self.func_registry:
            message='Error: Attempt to invoke unregistered mode |%s|' % (mode)
            _1CH.log_error(message)
            raise Exception(message)
            
        args=[]
        kwargs={}
        unused_args=queries.copy()
        if self.args_registry[mode]:
            # positional arguments are all required
            for arg in self.args_registry[mode]:
                arg=arg.strip()
                if arg in queries:
                    args.append(queries[arg])
                    del unused_args[arg]
                else:
                    message='Error: mode |%s| requested argument |%s| but it was not provided.' % (mode, arg)
                    _1CH.log_error(message)
                    raise Exception(message)
            
        if self.kwargs_registry[mode]:
            #kwargs are optional
            for arg in self.kwargs_registry[mode]:
                arg=arg.strip()
                if arg in queries:
                    kwargs[arg]=queries[arg]
                    del unused_args[arg]
        
        if 'mode' in unused_args: del unused_args['mode'] # delete mode last in case it's used by the target function
        _1CH.log('Calling |%s| for mode |%s| with pos args |%s| and kwargs |%s|' % (self.func_registry[mode].__name__, mode, args,  kwargs))
        if unused_args:_1CH.log('Warning: Arguments |%s| were passed but unused by |%s| for mode |%s|' % (unused_args, self.func_registry[mode].__name__, mode))
        self.func_registry[mode](*args, **kwargs)
