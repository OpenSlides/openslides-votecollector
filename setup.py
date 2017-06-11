from setuptools import find_packages, setup

package_name = 'openslides-votecollector'
module_name = 'openslides_votecollector'

module = __import__(module_name)

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as requirements:
    install_requires = requirements.readlines()

setup(
    name=package_name,
    author='Authors of %s, see AUTHORS' % module.__verbose_name__,
    author_email='support@openslides.org',
    description=module.__verbose_name__,
    license='MIT',
    long_description=long_description,
    url='https://openslides.org/',
    version=module.__version__,

    keywords='OpenSlides',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=install_requires,
    entry_points={'openslides_plugins': '%s = %s' % (module.__verbose_name__, module_name)})
