import setuptools

REQUIRED_PACKAGES = ['vk-api', 'yandex-music', 'spotipy']

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Move-My-Music",
    version="0.0.2dev1",
    author="Max Medvedev",
    author_email="medve.mk@gmail.com",
    description="Script to migrate music between platforms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Addic7edBoy/MoveMyMusic",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': ['MMM=MoveMyMusic.__main__:main'],
    }
)
