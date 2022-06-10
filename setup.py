import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="system2mqtt", # Replace with your own username
    version="0.5.1",
    author="OptimusGREEN",
    author_email="root@optimusgreen.com",
    description="send system info to mqtt",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/optimusgreen/system2mqtt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['paho-mqtt',
                      'psutil',
                      'requests',
                      'python-dotenv'
        ],
)