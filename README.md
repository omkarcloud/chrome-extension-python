# Chrome Extension Python

`Chrome Extension Python` that allows you to easily integrate Chrome extensions in web automation frameworks like Botasaurus, Selenium, and Playwright. 

This tool simplifies the process of downloading, configuring, and using any Chrome extension.

## Installation

Install the package using pip:

```bash
python -m pip install chrome_extension_python
```

## Usage

This package allows the use of Chrome extensions in Botasaurus, Selenium, and Playwright frameworks.

Below are examples demonstrating the integration of the Adblock extension in each framework.

### Usage with Botasaurus

[Botasaurus](https://github.com/omkarcloud/botasaurus), a web scraping framework, integrates easily with `Chrome Extension Python`. Pass the Chrome Webstore link of the extension to use it.

Example with Adblock Extension:

```python
from botasaurus.browser import browser, Driver
from chrome_extension_python import Extension

@browser(
    extensions=[
        # Simply pass the Chrome Extension Link
        Extension(
            "https://chromewebstore.google.com/detail/adblock-%E2%80%94-best-ad-blocker/gighmmpiobklfepjocnamgkkbiglidom"
        )
    ],
)
def scrape_while_blocking_ads(driver: Driver, data):
    driver.prompt()

scrape_while_blocking_ads()
```

### Usage with Selenium

Integration with Selenium involves setting up Chrome options and adding the extension.

Example:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_autoinstaller import install
from chrome_extension_python import Extension

# Set Chrome options
options = Options()
options.add_argument(Extension("https://chromewebstore.google.com/detail/adblock-%E2%80%94-best-ad-blocker/gighmmpiobklfepjocnamgkkbiglidom").load())

# Install and set up the driver
driver_path = install()
driver = webdriver.Chrome(driver_path, options=options)

# Prompt for user input
input("Press Enter to exit...")

# Clean up
driver.quit()
```

### Usage with Playwright

Playwright integration includes specifying the extension path and launching the browser context with the extension.

Example:

```python
from playwright.sync_api import sync_playwright
from chrome_extension_python import Extension
import random

def generate_random_profile():
    return str(random.randint(1, 1000))

with sync_playwright() as p:
    extension_path = Extension("https://chromewebstore.google.com/detail/adblock-%E2%80%94-best-ad-blocker/gighmmpiobklfepjocnamgkkbiglidom").load(with_command_line_option=False)
    browser = p.chromium.launch_persistent_context(
        user_data_dir=generate_random_profile(),
        headless=False,
        args=[
            '--disable-extensions-except='+ extension_path,
            '--load-extension=' + extension_path,
        ],
    )
    page = browser.new_page()
    input("Press Enter to exit...")
    browser.close()
```

## Configuring an Extension

Extensions can be configured either

- by editing their JavaScript files
- or by interacting with their UI using Selenium.

### Editing JavaScript Files

The JavaScript file editing method is faster and more robust. The following example demonstrates creating a configurable CapSolver Extension with an API key:

```python
from chrome_extension_python import Extension

class Capsolver(Extension):
    def __init__(self, api_key):
        # Initialize the Capsolver extension with given parameters
        super().__init__(
            extension_id="pgojnojmmhpofjgdmaebadhbocahppod",  # Unique identifier for the Chrome Extension, found in the Chrome Webstore link
            extension_name="capsolver",  # The name assigned to the extension
            api_key=api_key,  # An important custom parameter (API key) required for the extension's functionality
        )

    # This method is called to update the necessary JavaScript files within the extension
    def update_files(self, api_key):
        # Retrieve a list of all JavaScript files in the extension
        js_files = self.get_js_files()

        def update_js_contents(content):
            # A string in the JavaScript file that needs to be replaced
            to_replace = "return e.defaultConfig"
            # The new content to insert, which includes the API key
            replacement = (
                f"return {{ ...e.defaultConfig, apiKey: '{api_key}' }}"
            )
            # Replace the old string with the new one in the file's content
            return content.replace(to_replace, replacement)

        # Loop through each JavaScript file and update its contents
        for file in js_files:
            file.update_contents(update_js_contents)

        def update_config_contents(content):
            # Replace the empty apiKey value with the new API key in the config file
            key_replaced = content.replace("apiKey: '',", f"apiKey: '{api_key}',")

            return key_replaced

        # Retrieve the specific configuration JavaScript file
        config_file = self.get_file("/assets/config.js")

        # Update the config file with the new API key
        config_file.update_contents(update_config_contents)
```

Usage Example:

```python
from botasaurus.browser import browser, Driver
from chrome_extension_python import Extension

@browser(
    extensions=[
        # Simply pass the Chrome Extension Link
        Capsolver(api_key="CAP-MY_KEY")
    ],
)
def open_chrome(driver: Driver, data):
    driver.get("https://recaptcha-demo.appspot.com/recaptcha-v2-checkbox.php")
    driver.prompt()

open_chrome()
```

## API Reference

For custom extension development, the following methods are available:

- `get_js_files`, `get_json_files`, `get_html_files`, `get_css_files`: Recursively retrieves specified file types.
- `get_file`: Retrieves a specific file as a `File` object.
- `File.update_contents`: Updates the content of a file.
- `force_update` (defaults to False): Redownload the extension and call `update_files` when extension data changes. It is recommended to set it to `True` during active development.

Example of a custom extension with `force_update`:

```python
from chrome_extension_python import Extension

class CustomExtension(Extension):
    def __init__(self, api_key):
        # Initialize the CustomExtension with specific parameters
        super().__init__(
            extension_id="pgojnojmmhpofjgdmaebadhbocahppod", # Unique identifier for the Chrome Extension, obtained from the Chrome Webstore link
            extension_name="capsolver", # The name assigned to the extension
            force_update=True, # This flag, when set to True, forces the redownload of the extension and calls the `update_files` method. This is useful during development to ensure updates are applied.
        )
```

## Examples of Custom Extensions
Here are some code snippets of Custom Extensions to provide you with an idea of how to develop your own.

- [Capsolver Extension](https://github.com/omkarcloud/capsolver-extension-python/blob/master/capsolver_extension_python/__init__.py)
- [2captcha Extension](https://github.com/omkarcloud/twocaptcha-extension-python/blob/master/twocaptcha_extension_python/__init__.py)

## Publishing Your Extension

If you wish to share your extension with other developers via PyPI, follow these steps:

1. Clone the template repository: [capsolver-extension-python](https://github.com/omkarcloud/capsolver-extension-python).
2. Replace references to "capsolver" with your extension's name.
3. Rename the `capsolver_extension_python` folder to match your extension name.
4. Insert your extension code in `__init__.py`.
5. Update README.md
6. Use `npm run upload` to publish the extension on PyPI.

Contact us at `chetan@omkar.cloud` with details about your extension. If it's beneficial for web scrapers, we'll promote it within the Botasaurus community.

## Love It? [Star It ⭐!](https://github.com/omkarcloud/chrome-extension-python)

Become one of our amazing stargazers by giving us a star ⭐ on GitHub!

It's just one click, but it means the world to me.

[![Stargazers for @omkarcloud/chrome-extension-python](https://bytecrank.com/nastyox/reporoster/php/stargazersSVG.php?user=omkarcloud&repo=chrome-extension-python)](https://github.com/omkarcloud/chrome-extension-python/stargazers)
