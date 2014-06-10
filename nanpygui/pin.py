from traits.has_traits import HasTraits
from traits.trait_types import Str
from traits.trait_types import Any
from traits.trait_types import Enum
from traits.trait_types import Bool
from traits.trait_types import Range
from traitsui.editors.range_editor import RangeEditor
from traitsui.group import HGroup
from traitsui.item import Item
from traitsui.view import View

INPUT, OUTPUT = 0, 1


class PinWrapper(HasTraits):
    pin = Any()
    function = Any()
    usb = Any()
    timer = Any()
    initmode = False
    avr_pin = Any()

    def _pin_changed(self):
        self.initmode = True
        self.name = self.pin.name
        self.mode = ['INPUT', 'OUTPUT'][self.pin.read_mode()]
        if self.mode == 'OUTPUT':
            # TODO:
            self.digital_output = bool(self.pin.read_digital_value())
        self.function = self.pin.programming_function
        if hasattr(self.pin, 'is_usb_plus'):
            self.usb = ['', '+', '-'][self.pin.is_usb_plus + 2 *
                                      self.pin.is_usb_minus]
        else:
            self.usb = ''

        if self.pin.pwm.available:
                ls = [int(x) for x in self.pin.pwm.frequencies_available]
                self.add_trait('pwm_frequency', Enum(ls))
                self.pwm_frequency = int(self.pin.pwm.frequency)
                self.timer = self.pin.pwm.timer_register_name_b

        self.avr_pin = self.pin.avr_pin

        self.initmode = False

    def _pwm_frequency_changed(self):
        self.pin.pwm.frequency = self.pwm_frequency

    pwm_output = Range(0, 255)

    def _pwm_output_changed(self):
        self.pin.pwm.write_value(self.pwm_output)

    pwm = Bool()

    def _pwm_changed(self):
        if self.pwm:
            self._pwm_output_changed()
        else:
            self._digital_output_changed()

    name = Str()
    mode = Enum(['INPUT', 'OUTPUT'])

    def _mode_changed(self):
        if not self.initmode:
            self.pin.write_mode(OUTPUT if (self.mode == 'OUTPUT') else INPUT)
    pullup = Bool()

    def _pullup_changed(self):
        self.pin.write_pullup(self.pullup)
    digital_input = Bool()
    digital_output = Bool()

    def _digital_output_changed(self):
        if not self.initmode:
            # TODO:
            self.pin.write_digital_value(self.digital_output)

    analog_input = Any()
#     voltage = Any()

    def update(self):
        ''
        if self.mode == 'INPUT':
            self.analog_input = self.pin.analog_value
#             self.voltage = an.voltage

            self.digital_input = bool(self.pin.read_digital_value())

    traits_view = View(
        HGroup(
            Item('name',
                 show_label=False,
                 style='readonly',
                 ),
            Item('avr_pin',
                 show_label=False,
                 style='readonly',
                 format_func=lambda x: '(%s)' % (x),

                 ),
            'mode',
            Item('pwm',
                 visible_when='mode=="OUTPUT"',
                 defined_when='pin.pwm.available',
                 ),
            HGroup(
                Item('digital_input',
                     defined_when='pin.is_digital',
                     enabled_when='0',
                     ),
                Item('analog_input',
                     defined_when='pin.is_analog',
                     style='readonly',
                     ),
                #                 Item('voltage',
                #                      defined_when='pin.is_analog',
                #                      style='readonly',
                #                      ),
                Item('pullup',
                     ),
                visible_when='mode=="INPUT"',
            ),
            Item('digital_output',
                 visible_when='mode=="OUTPUT" and not pwm',
                 ),
            HGroup(
                Item('pwm_frequency',
                     ),
                Item(name='pwm_output',
                     editor=RangeEditor(
                         mode='slider',
                         low=0,
                         high=255,
                     ),
                     style='custom',
                     ),
                visible_when='mode=="OUTPUT" and pwm',
                defined_when='pin.pwm.available',
            ),
            Item('timer',
                 defined_when='timer',
                 style='readonly',
                 ),
            Item('function',
                 defined_when='function',
                 style='readonly',
                 ),
            Item('usb',
                 defined_when='usb',
                 style='readonly',
                 ),
        ),
    )
