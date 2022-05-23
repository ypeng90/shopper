"""Generate Captcha from given text in PNG or given format"""

import os
import random
from io import BytesIO
from PIL import Image, ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype

ALL_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Bezier:
    """Bezier curve class"""
    
    def __init__(self):
        self._tsequence = tuple([t / 20.0 for t in range(21)])
        self._beziers = {}

    def generate(self, n):
        """Generate with given number

        Args:
            n (int): input number

        Returns:
            list: list of coefficients
        """
        if n not in self._beziers:
            combinations = self._pascal_row(n - 1)
            result = []
            for t in self._tsequence:
                tpowers = (t ** i for i in range(n))
                upowers = ((1 - t) ** i for i in range(n - 1, -1, -1))
                coefs = [c * t * u for c, t, u in zip(combinations, tpowers, upowers)]
                result.append(coefs)
            self._beziers[n] = result
        return self._beziers[n]

    @staticmethod
    def _pascal_row(n):
        """Generate nth row in Pascal triangle

        Args:
            n (int): nth row

        Returns:
            list: nth row
        """
        row = [1]
        x, numerator = 1, n
        for denominator in range(1, n // 2 + 1):
            x *= numerator
            x /= denominator
            row.append(x)
            numerator -= 1
        if n & 1:
            row.extend(reversed(row))
        else:
            row.extend(reversed(row[:-1]))
        return row


class Captcha:
    """Captcha class"""

    def __init__(self, width=200, height=75):
        """

        Args:
            width (int, optional): width of desired image. Defaults to 200.
            height (int, optional): height of desired image. Defaults to 75.
        """
        self._bezier = Bezier()
        self._fonts = [os.path.join(
            os.path.dirname(__file__),
            "fonts",
            "DroidSansMono.ttf"
        )]
        self._width, self._height = width, height
        self._image = None

    @property
    def _color(self):
        """Color for text, curve, and noise

        Returns:
            tuple: color of (red, green, blue, opacity)
        """
        return self._random_color(100, 150, random.randint(100, 150))

    @staticmethod
    def _random_color(start=0, end=255, opacity=None):
        """Generate random color in range [start, end]

        Args:
            start (int, optional): start of range. Defaults to 0.
            end (int, optional): end of range. Defaults to 255.
            opacity (int, optional): opacity. Defaults to None.

        Returns:
            tuple: color of (red, green, blue[, opacity])
        """
        red = random.randint(start, end)
        green = random.randint(start, end)
        blue = random.randint(start, end)
        if opacity is None:
            return red, green, blue
        return red, green, blue, opacity

    def _background(self):
        """Generate background of image
        """
        Draw(self._image).rectangle(
            [(0, 0), self._image.size],
            # larger number means lighter background
            fill=self._random_color(245, 255)
        )

    def _text(self, captcha_text, drawings=None, squeeze_factor=0.75):
        """Generate text with given drawings effects

        Args:
            captcha_text (str): captcha text
            drawings (list, optional): list of desired effects. Defaults to None.
            squeeze_factor (float, optional): squeeze factor (larger means more
                                              separated from each other). Defaults to 0.75.
        """
        fonts = tuple([truetype(name, size)
                       for name in self._fonts
                       for size in (65, 70, 75)])
        drawings = drawings or ["_twist", "_rotate", "_shift"]
        draw = Draw(self._image)

        char_images = []
        for c in captcha_text:
            font = random.choice(fonts)
            c_width, c_height = draw.textsize(c, font=font)
            char_image = Image.new("RGB", (c_width, c_height), (0, 0, 0))
            char_draw = Draw(char_image)
            char_draw.text((0, 0), c, font=font, fill=self._color)
            char_image = char_image.crop(char_image.getbbox())
            for drawing in drawings:
                d = getattr(self, drawing)
                char_image = d(char_image)
            char_images.append(char_image)

        width, height = self._image.size
        total = sum(int(i.size[0] * squeeze_factor) for i in char_images[:-1])
        offset = int((width - total - char_images[-1].size[0]) / 2)
        for char_image in char_images:
            c_width, c_height = char_image.size
            mask = char_image.convert("L").point(lambda i: i * 1.97)
            self._image.paste(
                char_image,
                (offset, int((height - c_height) / 2)),
                mask
            )
            offset += int(c_width * squeeze_factor)

    @staticmethod
    def _twist(image, dx_factor=0.3, dy_factor=0.3):
        """Twist image"""
        
        width, height = image.size
        dx = width * dx_factor
        dy = height * dy_factor
        x1 = int(random.uniform(-dx, dx))
        y1 = int(random.uniform(-dy, dy))
        x2 = int(random.uniform(-dx, dx))
        y2 = int(random.uniform(-dy, dy))
        twisted = Image.new(
            "RGB",
            (width + abs(x1) + abs(x2), height + abs(y1) + abs(y2))
        )
        twisted.paste(image, (abs(x1), abs(y1)))
        width2, height2 = twisted.size
        return twisted.transform(
            (width, height),
            Image.QUAD,
            (x1, y1, -x1, height2 - y2, width2 + x2, height2 + y2, width2 - x2, -y1)
        )

    @staticmethod
    def _shift(image, dx_factor=0.1, dy_factor=0.2):
        """Shift image"""
        
        width, height = image.size
        dx = int(random.random() * width * dx_factor)
        dy = int(random.random() * height * dy_factor)
        shifted = Image.new("RGB", (width + dx, height + dy))
        shifted.paste(image, (dx, dy))
        return shifted

    @staticmethod
    def _rotate(image, angle=25):
        """Rotate image"""
        
        rotated = image.rotate(
            random.uniform(-angle, angle),
            Image.BILINEAR,
            expand=1
        )
        return rotated

    def _curve(self, width=4, number=6):
        """Generate noise Bezier curve

        Args:
            width (int, optional): width of Bezier curve. Defaults to 4.
            number (int, optional): parameter of Bezier curve. Defaults to 6.
        """
        dx, height = self._image.size
        dx /= number
        path = [(dx * i, random.randint(0, height)) for i in range(1, number)]
        bcoefs = self._bezier.generate(number - 1)
        points = []
        for coefs in bcoefs:
            t = tuple(sum([coef * p for coef, p in zip(coefs, ps)]) for ps in zip(*path))
            points.append(t)
        Draw(self._image).line(points, fill=self._color, width=width)

    def _noise(self, number=100, size=2):
        """Generate noise dots

        Args:
            number (int, optional): number of noise dots. Defaults to 100.
            size (int, optional): size of noise dots. Defaults to 2.
        """
        width, height = self._image.size
        dx, dy = width / 10, height / 10
        width, height = width - dx, height - dy
        draw = Draw(self._image)
        color = self._color
        for i in range(number):
            x = int(random.uniform(dx, width))
            y = int(random.uniform(dy, height))
            draw.line(
                ((x, y), (x + size, y)),
                fill=color,
                width=size
            )

    def _smooth(self):
        """Smooth image"""
        
        self._image.filter(ImageFilter.SMOOTH)

    def generate(self, fmt="PNG"):
        """Generate Captcha image

        Args:
            fmt (str, optional): format of image. Defaults to "PNG".

        Returns:
            (str, bytes): Captcha text as str, Captcha image as bytes
        """
        captcha_text = "".join(random.choices(ALL_CHARS, k=4))
        self._image = Image.new("RGB", (self._width, self._height), (255, 255, 255))
        self._background()
        self._text(captcha_text)
        self._curve()
        self._noise()
        self._smooth()
        image_bytes = BytesIO()
        self._image.save(image_bytes, format=fmt)
        return captcha_text, image_bytes.getvalue()
