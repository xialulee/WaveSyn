# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:45:33 2014

@author: Feng-cong Li
"""
from numpy import array, ndarray, angle, log10, convolve, fft, r_, conj
from tkinter import Frame, IntVar
from tkinter.ttk import Button, Checkbutton, Progressbar, Combobox


from wavesynlib.widgets.tk import Group, LabeledEntry
from wavesynlib.widgets.classselector import ask_class_name
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.languagecenter.utils import set_attributes
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer
from wavesynlib.mathtools import Algorithm, AlgorithmDict, AlgorithmNode, DataContainer, Expression

import json



class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = kwargs.pop('wavesyn_root')   
        self.__topwin = kwargs.pop('topwin')

        super().__init__(*args, **kwargs)
                
        parameter_frame    = Frame(self)
        parameter_frame.pack(side='left', expand='yes', fill='y')
        self.__num = LabeledEntry(parameter_frame)
        set_attributes(self.__num,
            label_text   = 'num',
            entry_text   = '1',
            label_width  = 5,
            entry_width  = 8,
            checker_function   = self._app.gui.value_checker.check_int
        )
        self.__num.entry.bind('<Return>', lambda event: self._on_solve_click())
        self.__num.pack(side='top')

        self.__pci  = LabeledEntry(parameter_frame)
        set_attributes(self.__pci,
            label_text   = 'PCI',
            entry_text   = '100',
            label_width  = 5,
            entry_width  = 8,
            checker_function = self._app.gui.value_checker.check_int
        )
        self.__pci.pack(side='top')
        
        self.__parallel_checker_variable    = IntVar()
        self.__parallel_checker  = Checkbutton(parameter_frame, text="Parallel", variable=self.__parallel_checker_variable, command=self._on_parallel_checker_click)
        self.__parallel_checker.pack()
        
        progfrm = Frame(self)
        progfrm.pack(side='left', expand='yes', fill='y')

        self.__genbtn = Button(progfrm, text='Generate', command=self._on_solve_click)
        self.__genbtn.pack(side='top')  
        Button(progfrm, text='Stop', command=self._on_stop_button_click).pack(side='top')         
        
        self.__progressbar_variable = IntVar()
        self.__finishedwav = IntVar()        
        self.__progressbar = Progressbar(progfrm, orient='horizontal', variable=self.__progressbar_variable, maximum=100)
        self.__progressbar.pack(side='left')
        self.__progressbar.config(length=55)   
        self.__finishedwavbar = Progressbar(progfrm, orient='horizontal', variable=self.__finishedwav)
        self.__finishedwavbar.pack(side='left')
        self.__finishedwavbar.config(length=30)  

        self.name = 'Generate'

        self.getparams = None
        self.__stopflag = False

        
    def _on_solve_click(self):
        params = self.__topwin.parameter_group.get_parameters()
        repeat_times = self.__num.get_int()   
        
        if self.__parallel_checker_variable.get():
            run = self.__topwin.current_algorithm.process_run
        else:
            run = self.__topwin.current_algorithm.thread_run
        with code_printer():
            run(on_finished=['store', 'plot'], progress_indicator='progress_dialog', repeat_times=repeat_times, **params)


    def _on_stop_button_click(self):
        self.__stopflag = True
        
        
    def _on_parallel_checker_click(self):
        topwin = self.__topwin
        if topwin.current_algorithm.need_cuda:
            self.__parallel_checker_variable.set(0)
            topwin.root_node.gui.dialogs.report(f'''{topwin.node_path}:
Current algorithm "{topwin.current_algorithm.meta.name}" need CUDA worker, which does not support multi-cpu parallel.
            ''')
            
            
    def _cancel_parallel(self):
        self.__parallel_checker_variable.set(0)
                


class ParamsGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = kwargs.pop('wavesyn_root')
        self.__topwin   = kwargs.pop('topwin')
        self.balloon    = self._app.gui.balloon

        super().__init__(*args, **kwargs)
        self.__algo = None
        self.__MAXROW = 3
        self.__params = {}  

        self.__frameDict    = {}
          
        self.name = 'Parameters'
        

    def append_algorithm(self, algorithm):
        #To do: when algo is reset, the frm should be removed
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()
        frm = Frame(self)
        frm.pack()
        paramInfo   = {}
        params = algorithm['parameters']
        for index, name in enumerate(params):
            param = params[name]
            paramitem = LabeledEntry(frm)
            paramitem.label_text = name
            paramitem.label_width = 5
            paramitem.entry_width = 8
            if self.balloon:
                tip = f'''{param.shortdesc}

Type: {param.type.__name__}.'''
                self.balloon.bind_widget(paramitem.label, balloonmsg=tip)
            if param.type is int:
                paramitem.checker_function = self._app.gui.value_checker.check_int
            elif param.type is float:
                paramitem.checker_function = self._app.gui.value_checker.check_float
            paramitem.grid(row=index%self.__MAXROW, column=index//self.__MAXROW)
            #self.__params[param.name] = {'gui':paramitem, 'meta':param}
            paramInfo[param.name] = {'gui':paramitem, 'meta':param}
        self.__algo = algorithm
        #self.__frameDict[algorithm.meta.name]   = frm
        self.__frameDict[algorithm['name']]   = dict(frame=frm, paramInfo=paramInfo)
        self.__params   = paramInfo
        

    def get_parameters(self):
        params = self.__params
        convert = {int:int, float:float, Expression:Expression.converter, '':lambda x: x}
        return {name: convert[params[name]['meta'].type](params[name]['gui'].entry_text) for name in params}
        
        
    def change_algorithm(self, algorithmName):
        for algoName in self.__frameDict:
            self.__frameDict[algoName]['frame'].pack_forget()        
        self.__frameDict[algorithmName]['frame'].pack()
        self.__params   = self.__frameDict[algorithmName]['paramInfo']
        
     
     
class AlgoSelGroup(Group):
    def __init__(self, *args, **kwargs):
        self._topwin  = kwargs.pop('topwin')
        super().__init__(*args, **kwargs)
        
        self.__algorithm_list = Combobox(self, value=[], takefocus=1, stat='readonly', width=12)
        self.__algorithm_list['values']   = []
        self.__algorithm_list.pack()
        self.__algorithm_list.bind('<<ComboboxSelected>>', self._on_algorithm_change)
        
        Button(self, text='Load Algorithm', command=self._on_load_algorithm).pack()
        Button(self, text='Reload', command=self._on_reload_algorithm).pack()
        
        self.name = 'Algorithms'          
        
        
    @property
    def algorithm_list(self):
        return self.__algorithm_list
        
        
    def _on_algorithm_change(self, event):
        self._topwin.change_algorithm(event.widget.get())
        
        
    def _on_load_algorithm(self):        
        new_thread_do = self._topwin.root_node.thread_manager.new_thread_do
        main_thread_do = self._topwin.root_node.thread_manager.main_thread_do
    
        @new_thread_do
        def select_and_load():
            class_info = ask_class_name('wavesynlib.algorithms', Algorithm)
            if not class_info:
                return
            module_name, class_name = class_info
            if isinstance(module_name, bytes):
                module_name = module_name.decode('utf-8')
            if isinstance(class_name, bytes):
                class_name = class_name.decode('utf-8')
            @main_thread_do()
            def load():
                with code_printer():
                    self._topwin.load_algorithm(module_name=module_name, class_name=class_name)
            
            
    def _on_reload_algorithm(self):
        with code_printer():
            self._topwin.current_algorithm.reload_algorithm()



class SingleWindow(FigureWindow, DataContainer):      
    window_name  = 'WaveSyn-SingleSyn' 

    _xmlrpcexport_  = ['load_algorithm']
       
    def __init__(self, *args, **kwargs):     
        FigureWindow.__init__(self, *args, **kwargs)
        self.current_data    = None
        
        
    def on_connect(self):
        # algorithm dict and current data
        self.algorithms = AlgorithmDict()
        self.lock_attribute('algorithms')
        #        
        
        # The toolbar
        tool_tabs = self._tool_tabs
        figure_book = self.figure_book
        
        frmAlgo = Frame(tool_tabs)
        algorithm_selection_group  = AlgoSelGroup(frmAlgo, topwin=self)
        algorithm_selection_group.pack(side='left', fill='y')
        
        parameter_group = ParamsGroup(frmAlgo, topwin=self, wavesyn_root=self.root_node)
        parameter_group.pack(side='left', fill='y')
        
        solve_group = OptimizeGroup(frmAlgo, topwin=self, wavesyn_root=self.root_node)
        solve_group.pack(side='left', fill='y')
        tool_tabs.add(frmAlgo, text='Algorithm')
        
        with self.attribute_lock:
            set_attributes(self,
                algorithm_selection_group = algorithm_selection_group,
                parameter_group = parameter_group,
                solve_group = solve_group                         
            )
                
        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        self._make_window_manager_tab()
        # End toolbar
        figure_book.make_figures(
            figure_meta  = [
                dict(name='Envelope', polar=False),
                dict(name='Phase', polar=False),
                dict(name='AutoCorrelation', polar=False),
                dict(name='PSD', polar=False)
            ]
        )
        
        with open(self.root_node.config_file_path) as f:
            config  = json.load(f)
        algorithms  = config['SingleWaveformAlgorithms']

        for algo in algorithms:
            self.load_algorithm(module_name=algo['ModuleName'], class_name=algo['ClassName'])

        self.algorithm_selection_group.algorithm_list.current(len(algorithms)-1)
        
        envelope_figure = figure_book[0]
        envelope_figure.plot_function  = lambda current_data, *args, **kwargs:\
            envelope_figure.plot(abs(current_data), *args, **kwargs)
        
        phase_figure = figure_book[1]
        phase_figure.plot_function   = lambda current_data, *args, **kwargs:\
            phase_figure.plot(angle(current_data), *args, **kwargs)
            
        def plot_acdb(current_data, *args, **kwargs):
            s   = current_data
            if not isinstance(s, ndarray):
                s   = array(s)
            N       = len(s)
            ac      = convolve(s, conj(s[::-1]))
            acdb    = 20*log10(abs(ac))
            acdb    = acdb - max(acdb)
            autocorrelatino_figure.plot(r_[(-N+1):N], acdb, *args, **kwargs)            
            
        autocorrelatino_figure     = figure_book[2]
        autocorrelatino_figure.plot_function    = plot_acdb
            
        psd_figure      = figure_book[3]
        psd_figure.plot_function     = lambda current_data, *args, **kwargs:\
            psd_figure.plot(abs(fft.fft(current_data)), *args, **kwargs)
            
    
    @Scripting.printable        
    def load_algorithm(self, module_name, class_name):
        node = AlgorithmNode(module_name, class_name)
        self.algorithms.add(node)
        values = self.algorithm_selection_group.algorithm_list['values']
        if values == '':
            values  = []
        if isinstance(values, tuple):
            values  = list(values)
        values.append(node['name'])
        self.algorithm_selection_group.algorithm_list['values']  = values
        self.algorithm_selection_group.algorithm_list.current(len(values)-1)
        self.parameter_group.append_algorithm(node)
        self.solve_group._cancel_parallel()
        return node.meta.name

        
    def change_algorithm(self, algorithmName):
        self.parameter_group.change_algorithm(algorithmName)
        self.solve_group._cancel_parallel()

        
    @property
    def current_algorithm(self):
        return self.algorithms[self.algorithm_selection_group.algorithm_list.get()]
            
