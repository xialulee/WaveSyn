from tkinter import *
from tkinter.ttk import Label, Scale, Entry, Button, Scrollbar, Treeview, Combobox
from wavesynlib.widgets.tk.group import Group



load_grp = {
    "class": Group, 
    "name": "load_grp", 
    "pack": {
        "side": LEFT,
        "fill": Y
    }, 
    "setattr": {
        "name": "Load"
    }, 
    "children": [
        {
            "class": Button,
            "name": "load_btn", 
            "init": {
                "text": "Load"
            }
        }
    ]
}

export_grp = {
    "class": Group, 
    "name": "export_grp", 
    "pack": {
        "side": LEFT,
        "fill": Y
    }, 
    "setattr": {
        "name": "Resize"
    }, 
    "children": [
        {
            "class": Button, 
            "name": "export_all_btn", 
            "init": {
                "text": "All Layers"
            },
            "pack": {
                "fill": X
            }
        }, 
        {
            "class": Button, 
            "name": "export_selected_btn",
            "init": {
                "text": "Selected Layer/Group"
            }
        }
    ]
}

resize_grp = {
    "class": Group, 
    "name": "resize_grp", 
    "pack": {
        "side": LEFT,
        "fill": Y
    }, 
    "setattr": {
        "name": "Resize"
    }, 
    "children": [
        {
            "class": Scale,
            "name": "image_scale", 
            "init": {
                "from_": 5, 
                "to": 100, 
                "orient": HORIZONTAL, 
                "value": 100
            }
        }, 
        {
            "class": Label, 
            "name": "scale_label",
            "init": {
                "text": "100%"
            }
        }
    ]
}

external_viewer_grp = {
    "class": Group, 
    "name": "external_viewer_grp",
    "pack": {
        "side": LEFT, "fill": Y
    }, 
    "setattr": {
        "name": "Viewer"
    },
    "children": [
        {
            "class": Button, 
            "name": "launch_viewer_btn", 
            "init": {
                "text": "Launch"
            }
        }
    ]
}

wallpaper_grp = {
    "class": Group, 
    "name": "wallpaper_grp", 
    "pack": {
        "side": LEFT, "fill": Y
    }, 
    "setattr": {
        "name": "Wallpaper"
    }, 
    "children": [
        {
            "class": Button, 
            "name": "set_wallpaper_btn", 
            "init": {
                "text": "Set"
            }
        },
        {
            "class": Combobox, 
            "name": "wallpaper_position_combo", 
            "init": {
                "stat": "readonly", 
                "values": [
                    "Center", 
                    "Tile", 
                    "Stretch", 
                    "Fit", 
                    "Fill",
                    "Span"
                ]
            }
        }
    ]
}
