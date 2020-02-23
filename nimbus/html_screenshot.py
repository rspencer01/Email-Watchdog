"""Get screenshots of html code."""
import tempfile

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

BOOTSTRAP_FORMAT = """
<html>
<head>
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
</head>
<body style="padding:10px;">
{}
</body>
</html>"""


def get_screenshot(html, size=(400, 500)) -> bytes:
    """Takes a screenshot of the html document."""
    fl = tempfile.NamedTemporaryFile()
    fl.write(html)
    fl.seek(0)
    options = Options()
    options.headless = True
    driver = Firefox(options=options)
    driver.set_window_size(*size)
    driver.get("file:///{}".format(fl.name))
    png = driver.get_screenshot_as_png()
    driver.quit()
    fl.close()
    return png


png = get_screenshot(b"<html><body><h2>Headings</h2>Content</body></html>")
open("t.png", "wb").write(png)
