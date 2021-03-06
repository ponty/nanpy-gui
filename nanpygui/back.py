from threading import Thread
from traits.api import Bool
from traits.api import Instance
from traitsui.handler import Handler
from traitsui.ui_info import UIInfo
import os
import time
import traceback


class BackgroundHandler (Handler):

    # The UIInfo object associated with the UI:
    info = Instance(UIInfo)

    # Is the demo currently running:
    running = Bool(True)

    # Is the thread still alive?
    alive = Bool(True)

    def init(self, info):
        self.info = info
        Thread(target=self._update).start()

    def closed(self, info, is_ok):
        self.running = False
        while self.alive:
            time.sleep(.05)

    def _update(self):
        try:
            while self.running:
                self.loop()
                time.sleep(0.1)
        except Exception:
            traceback.print_exc()
            os._exit(1)
        self.alive = False

    def loop(self):
        ''
