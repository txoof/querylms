import setuptools

exec(open('QueryLMS/constants.py').read())


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="QueryLMS",
    version=QUERYLMS_VERSION,
    author="Aaron Ciuffo",
    author_email="aaron.ciuffo@gmail.com",
    description="Simple interface for making queries and issuing commands to Logitech Media Server and associated players",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/txoof/querylms",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent"],
    keywords="graphics e-paper display waveshare",
    install_requires=["requests"],
    project_urls={"Source": "https://github.com/txoof/querylms"},
    python_requires=">=3.7",
    package_data={"documentation": ["./docs"]},
)
