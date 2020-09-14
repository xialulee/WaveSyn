import json



def json_to_tk(parent, json_code, balloon=None):
    '''\
Example: [
    {"name":"alert_button", "class":"Button", "module":"ttk", 
    "init":{"text":"Alert!"}, "pack":{"fill":"x"}}
]
    '''
    import tkinter as tk
    import tkinter.ttk as ttk
    
    if isinstance(json_code, str):
        json_obj = json.loads(json_code)
    else:
        json_obj = json_code
    retval = {}

    for item in json_obj:
        if 'class' in item:
            class_name = item['class']
        else:
            class_name = item['class_']

        mod = item.get('module', None)
        if mod:
            mod = locals()[mod]
            cls = getattr(mod, class_name)            
        else:
            if isinstance(class_name, type):
                cls = class_name
            elif class_name in globals():
                cls = globals()[class_name]
            elif class_name in ttk.__dict__:
                cls = ttk.__dict__[class_name]
            else:
                cls = tk.__dict__[class_name]
        
        widget = cls(parent, **item.get('init', {}))
        if 'grid' in item:
            widget.grid(**item.get('grid', {}))        
        else:
            widget.pack(**item.get('pack', {}))
        
        if 'balloonmsg' in item and balloon is not None:
            balloon.bind_widget(widget, balloonmsg=item.get('balloonmsg'))
        
        if 'children' in item:
            sub_widgets = json_to_tk(widget, item.get('children'), balloon=balloon)
            for sub_widget in sub_widgets:
                if sub_widget in retval:
                    raise ValueError('Multiple widgets have a same name.')
                retval[sub_widget] = sub_widgets[sub_widget]
        if 'setattr' in item:
            attr_map = item.get('setattr')
            for attr_name in attr_map:
                setattr(widget, attr_name, attr_map[attr_name])
        if 'name' in item:
            retval[item.get('name')] = widget
    return retval



def hywidgets_to_tk(parent, hy_code, balloon=None):
    return json_to_tk(parent, hy_code, balloon)