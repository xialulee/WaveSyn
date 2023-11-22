from abc import ABC, abstractmethod


class KeyboardRGBController(ABC):
    """
    Abstract base class representing a controller for keyboard RGB lighting.

    This class provides an interface for setting the RGB light color of a keyboard.
    Specific implementations should be provided by subclasses for each specific
    keyboard vendor, utilizing their respective APIs.
    """

    @abstractmethod
    def set_color(self, color, key=None):
        """
        Abstract method to set the color of the keyboard's RGB lighting.

        Implementations of this method should change the color of the entire keyboard
        or a specific key if the key parameter is specified.

        Args:
            color:  The color to set. The format of this parameter can be
                    implementation-specific (e.g., a string like 'red', a hex code, or
                    an RGB tuple).
            key:    Optional; the specific key to change the color of. If not provided,
                    the color change applies to the entire keyboard. The format of this
                    parameter is implementation-specific and can depend on how individual
                    keys are addressed in the API of the specific keyboard vendor.

        Returns:
            None
        """


class RGBControl:
    """
    A class to control the RGB lighting of a keyboard.

    This class acts as a high-level interface for controlling keyboard RGB lighting,
    abstracting away the details of the specific keyboard vendor's API. It delegates
    the actual RGB control tasks to an instance of a subclass of KeyboardRGBController.

    Attributes:
        controller (KeyboardRGBController): An instance of a subclass of
                                            KeyboardRGBController that provides the
                                            specific implementation for controlling
                                            the RGB lighting of a keyboard.
    """

    def __init__(self, controller: KeyboardRGBController):
        """
        Initialize the RGBControl instance.

        Args:
            controller (KeyboardRGBController): An instance of a subclass of
                                                KeyboardRGBController that will be
                                                used to control the keyboard's RGB lighting.
        """
        self.controller = controller

    def set_color(self, color):
        """
        Set the color of the keyboard's RGB lighting.

        This method delegates the task of setting the color to the controller
        instance.

        Args:
            color:  The color to set. The format of this parameter should match the
                    expected format of the set_color method of the KeyboardRGBController
                    instance being used.
        """
        self.controller.set_color(color)


