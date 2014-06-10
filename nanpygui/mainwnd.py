from back import BackgroundHandler
from nanpy.arduinoapi import ArduinoApi
from nanpy.arduinotree import ArduinoTree
from nanpy.serialmanager import _auto_detect_serial_unix, SerialManager
from pin import PinWrapper
from traits.has_traits import HasTraits
from traits.trait_types import Any, Float, Bool, Enum, Instance, Int, List, \
    Range, Str, Date, Time, Button
from traitsui.editors.list_editor import ListEditor
from traitsui.editors.range_editor import RangeEditor
from traitsui.group import Group, HGroup, Tabbed
from traitsui.item import Item
from traitsui.message import message
from traitsui.view import View
import time
import traceback

# logging.basicConfig(level=logging.DEBUG)

INPUT, OUTPUT = 0, 1


def button(name, **kwargs):
    return Item(name=name,
                show_label=False,
                **kwargs
                )


class GuiDefine(HasTraits):
    name = Str()
    value = Str()
    traits_view = View(
        HGroup(
            Item('name',
                 width=200,
                 label='#define',
                 ),
            Item('value',
                 width=200,
                 show_label=False,
                 ),
        ),
    )


class Handler (BackgroundHandler):

    def loop(self):
        ''
        self.info.object.update()


class BoardWrapper(HasTraits):
    pins = List(PinWrapper)
    digital_pins = List(PinWrapper)
    analog_pins = List(PinWrapper)
    defines = List(GuiDefine)
    port_type = Enum('serial',
                     [
                         'none',
                         'serial',
                     ]
                     )
    serial_device = Enum(_auto_detect_serial_unix())
    baudrate = Int(115200)
    sleep_after_connect = Int(0)
    timeout = Int(1)
    uptime = Float()
    tree = None
    vcc = Float()
    avr_name = Str()
    arduino_version = Str()
    firmware_build_time = Str()
    gcc_version = Str()
    libc_version = Str()
    libc_date = Str()

    connected = Bool(False)
    connect = Button()
    disconnect = Button()

    def _connect_fired(self):
            try:
                connection = SerialManager(device=self.serial_device,
                                           baudrate=self.baudrate,
                                           sleep_after_connect=self.sleep_after_connect,
                                           timeout=self.timeout)
                connection.open()
                print ArduinoApi(connection=connection).millis()
            except Exception as e:
                traceback.print_exc()
                message(traceback.format_exc(), buttons=['OK'])
                return

            a = self.tree = ArduinoTree(connection=connection)

            d = a.define.as_dict
            s = [GuiDefine(name=k, value=str(v)) for k, v in d.items()]
            s.sort(key=lambda x: x.name)
            self.defines = s
            self.digital_pins = [PinWrapper(pin=a.pin.get(x))
                                 for x in a.pin.names_digital]
            self.analog_pins = [PinWrapper(pin=a.pin.get(x))
                                for x in a.pin.names_analog]
            self.pins = self.digital_pins + self.analog_pins

            fw = a.firmware_info
            self.arduino_version = fw.get('arduino_version')
            self.firmware_build_time = str(fw.get('compile_datetime'))
            self.avr_name = fw.get('avr_name')
            self.gcc_version = fw.get('gcc_version')
            self.libc_version = fw.get('libc_version')
            self.libc_date = str(fw.get('libc_date'))
            self.connected = True

    def _disconnect_fired(self):
            self.digital_pins = []
            self.analog_pins = []
            self.pins = []
            self.defines = []
            self.avr_name = ''
            self.arduino_version = ''
            self.firmware_build_time = ''
            self.gcc_version = ''
            self.libc_version = ''
            self.libc_date = ''

            self.tree.connection.close()
            del self.tree
            self.tree = None
            self.connected = False

    update_interval = Int(1000, desc='interval in msec')
    update_enable = Bool(True)

    def update(self):
        if self.update_enable and self.connected and self.tree:
            for x in self.pins:
                x.update()
            self.uptime = self.tree.api.millis() / 1000.0
            self.vcc = self.tree.vcc.read()
        time.sleep(self.update_interval / 1000.0)

    traits_view = View(
        Tabbed(
            Group(
                HGroup(
                    Group(
                        button('connect', enabled_when='not connected'),
                        button('disconnect', enabled_when='connected'),
                        Item(
                            'port_type', enabled_when='not connected', width=300,
                        ),
                        Group(
                            'serial_device',
                            'baudrate',
                            'sleep_after_connect',
                            'timeout',
                            visible_when='port_type=="serial"',
                            enabled_when='not connected',
                        ),
                    ),
                    Group(
                        'avr_name',
                        'arduino_version',
                        'firmware_build_time',
                        'gcc_version',
                        'libc_version',
                        'libc_date',
                        #                     'baudrate',
                        #                     'sleep_after_connect',
                        # visible_when='port_type=="serial"',
                        springy=True,
                    ),
                ),
                label='connection',
            ),
            Group(
                'uptime',
                'vcc',
                label='misc',
            ),
            Item(name='digital_pins',
                      editor=ListEditor(
                     style='custom',
                 ),
                 style='readonly',
                 show_label=False,
                 ),
            Item(name='analog_pins',
                      editor=ListEditor(
                 style='custom',
                 ),
                 style='readonly',
                 show_label=False,
                 ),
            Group(
                  'update_enable',
                Item(name='update_interval',
                     editor=RangeEditor(
                     mode='slider',
                     low=1,
                     high=1000,
                     ),
                     style='custom',
                     ),
                label='settings',
            ),
            Item('defines',
                show_label=False,
                editor=ListEditor(
#                     auto_size=False,
#                     editable=False,
#                     configurable=False,
                 style='custom',
                ),
                style='readonly',
                 )
        ),
        width=800,
        height=600,
        buttons=['Undo', 'Revert', 'OK', 'Cancel'],
        kind='live',
        resizable=True,
        handler=Handler(),
    )
