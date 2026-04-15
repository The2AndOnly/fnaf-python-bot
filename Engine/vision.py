import pyautogui as pg

class Vision:
    def __init__(self, COORDINATES):
        self.COORDINATES = COORDINATES
        pg.pixelMatchesColor = self._pixelMatchesColor
    
    def getPixel(self, coords, sc):
        width, height = sc.size
        return sc.getpixel((int(self.COORDINATES[coords][0] * width), int(self.COORDINATES[coords][1] * height)))

    # Monkey patch for pyautogui's "pixelMatchesColor" function
    def _pixelMatchesColor(self, x=0, y=0, expectedRGBColor=(0,0,0), tolerance=0, sample=None):
        
        if isinstance(x, pg.collections.abc.Sequence) and len(x) == 2:
            raise TypeError('pixelMatchesColor() has updated and no longer accepts a tuple of (x, y) values for the first argument. Pass these arguments as two separate arguments instead: pixelMatchesColor(x, y, rgb) instead of pixelMatchesColor((x, y), rgb)')

        pix = pg.pixel(x, y) if sample is None else sample
        
        if len(pix) != len(expectedRGBColor):
            assert False, (
                'Color mode was expected to be length 3 (RGB) or 4 (RGBA), but pixel is length %s and expectedRGBColor is length %s'  # noqa
                % (len(pix), len(expectedRGBColor))
            )
        return all(abs(a - b) <= tolerance for a, b in zip(pix, expectedRGBColor))
            