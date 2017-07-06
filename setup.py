from setuptools import setup, find_packages
setup(
      name="kong-cli",
      version="0.10.1",
      description="A command line client tools for Kong (http://getkong.org)",
      author="Simon / Jinyu LIU",
      author_email='simon.jinyu.liu@gmail.com',
      url="https://github.com/passos/kong-cli",
      license="Apache",
      packages=['kongcli'],
      scripts=["script/kong-cli"],
      install_requires=[
        'click>=6.0',
        'requests>=0.1.0',
        'simplejson>=3.10'
      ]
      )
