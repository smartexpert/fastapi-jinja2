import setuptools

# with open("README.md", "r", encoding="utf-8") as fh:
    # long_description = fh.read()

setuptools.setup(
    name='fastapi-jinja2',
    version='0.1.0',
    author='Shuaib Mohammad',
    author_email='smartexpert@users.noreply.github.com',
    description='Jinja2 integration for FastAPI',
    long_description='Adds integration of the Jinja2 template language to FastAPI via simple decorators',
    long_description_content_type="text/markdown",
    url='https://github.com/smartexpert/fastapi-jinja2',
    project_urls = {
        "Bug Tracker": "https://github.com/smartexpert/fastapi-jinja2/issues"
    },
    license='MIT',
    packages=['fastapi-jinja2'],
    install_requires=['fastapi','Jinja2'],
)