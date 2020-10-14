from typing import Any, Callable, List, Optional, Union

import cv2
from nptyping import NDArray, UInt8

BGRImage = NDArray[(Any, Any, 3), UInt8]
GrayImage = NDArray[(Any, Any), UInt8]
Image = Union[BGRImage, GrayImage]


class Pipeline(object):
    def __init__(self, image: Union[BGRImage, GrayImage], cache: bool = False):
        self.__base_img = image
        self.__head_img = image
        self.__head_idx = 0
        self.__cache = cache
        self.__cached_imgs: List[Image] = []

    def __rshift__(self, fn: Callable) -> "Pipeline":
        return self.apply(fn)

    def __rrshift__(self, fn: Callable) -> "Pipeline":
        return self.apply(fn)

    @property
    def base_img(self) -> Image:
        return self.__base_img

    @property
    def head_img(self) -> Image:
        return self.__head_img

    @property
    def head_idx(self) -> int:
        return self.__head_idx

    @property
    def cache(self) -> bool:
        return self.__cache

    def nth(self, nth: int) -> Optional[Image]:
        try:
            return self.__cached_imgs[nth]
        except IndexError:
            return None

    def nback(self, n: int) -> Optional[Image]:
        try:
            return self.__cached_imgs[-n]
        except IndexError:
            return None

    def apply(self, fn: Callable, *args, **kwargs) -> "Pipeline":
        prev_head = self.__head_img
        self.__head_img = fn(prev_head, *args, **kwargs)
        self.__head_idx += 1
        if self.cache:
            self.__cached_imgs.append(prev_head)
        return self

    def revert(self) -> "Pipeline":
        rev = self.nth(self.head_idx - 1)
        if rev is None:
            raise IndexError("Cannot revert anymore.")
        self.__head_idx -= 1
        self.__head_img = rev
        self.__cached_imgs = self.__cached_imgs[:self.__head_idx]
        return self

    def __close_img_window(self, press_close: bool) -> None:
        if press_close:
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def show_head(self, press_close: bool = True) -> None:
        cv2.imshow("Head", self.head_img)
        self.__close_img_window(press_close)

    def show_nth(self, nth: int, press_close: bool = True) -> None:
        img = self.nth(nth)
        if img is None:
            raise IndexError("Image does not found.")
        cv2.imshow(f"{nth} image", img)
        self.__close_img_window(press_close)

    def show_nback(self, n: int, press_close: bool = True) -> None:
        img = self.nback(n)
        if img is None:
            raise IndexError("Image does not found.")
        cv2.imshow(f"{n} back image", img)
        self.__close_img_window(press_close)
