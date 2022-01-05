import phue
import dataclasses
import typing
import json, requests, socket, os, sys
from Bridge import Bridge
from typing import (
    Any, Tuple, Dict, NoReturn, Optional, Union, List
)
from main import logger


@dataclasses.dataclass()
class Light:

    bridge: Bridge
    light_id: int

    alert: Optional[int] = None
    brightness: Optional[int] = None
    color_mode: Optional[str] = None
    color_temp: Optional[int] = None
    color_temp_k: Optional[int] = None
    effect: Optional[str] = None
    hue: Optional[int] = None
    reachable: Optional[bool] = False
    saturation: Optional[int] = None
    transition_time: Optional[int] = None
    type: Optional[str] = None
    xy: Optional[Union[List[int], Tuple[int]]] = None

    @property
    def name(self) -> str:
        return self.name

    @name.setter
    def name(self, new_name: str) -> NoReturn:

        old_name: str = ''.join(self.name)
        self._name = new_name
        self._set('name', self._name)


        logger.debug(
            f"Renaming peripheral from {old_name} to {new_name}."
        )

        ##self.bridge.lights_by_name[self.name] = self
        ## del self.bridge.lights_by_name[self.name]

    @property
    def on(self) -> bool:
        self._on = self._get('on')
        return self._on

    @on.setter
    def on(self, value: bool) -> NoReturn:

        if self._on and value is False:
            self._reset_brightness_after_on = self.transition_time is not None

            if self._reset_brightness_after_on:
                logger.warning(
                    "Turning peripheral off on the specified transition_time. Brightness will reset when on."
                )
        self._set('on', value)


        if self._on is False and value is True:
            self._reset_brightness_after_on = self.transition_time is not None

            if self._reset_brightness_after_on:
                logger.warning(
                    "Turning peripheral off on the specified transition_time. Brightness will reset when on."
                )
                self._reset_brightness_after_on = False

        self._on = value