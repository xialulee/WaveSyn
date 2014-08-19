Introduction of WaveSyn's scripting system
======
WaveSyn provides a scripting system for automation. The core of the system is a object model, shown as follows:
>wavesyn
>>console

>>clipboard

>>window[id]
>>>instance of PatternFitting window
>>>>figureBook

>>>instance of SingleSyn window
>>>>figureBook

>>>instance of MIMOSyn window
>>>>figureBook

The object model shown above is named "the model tree of WaveSyn". The root node of the tree is "wavesyn". One can access a node using the point; for example, "wavesyn.clipboard" corresponding to the clipboard node of wavesyn. Once a node is attached to the tree, it cannot be removed unless its parent is an instance of NodeDict or NodeList; for example, the "window" node of "wavesyn" is a instance of NodeDict, and its child node can be removed. 
