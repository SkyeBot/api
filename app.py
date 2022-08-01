from typing import Optional
from quart import Quart
import asyncpg
import os
import asyncio


class App(Quart):
    def __init__(self):
        super().__init__(__name__)


    def start(self, *, port: Optional[int]=None, debug: Optional[bool]=None):
        
        
        port = port or 5000
        debug = debug or False
    

        self.run(port=port, debug=debug)





