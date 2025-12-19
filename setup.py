from setuptools import setup
# get the version of moltenprot
# for alternative approaches see:
# https://packaging.python.org/guides/single-sourcing-package-version/
# versions are based on recommendations from https://semver.org/
with open('moltenprot/VERSION', 'r') as version_file:
    mp_version = version_file.read().strip()

'''
#NOTE Adding git hash is nice, but it will create a separate folder in site-packages. Since the hashes are random, it is not clear which of the versions is going to be installed. Also MoltenProt code relies on file VERSION to report version, which makes things further complicated. This code is kept here as the most appropriate place, but will not be enabled.

# if inside a git repo, append the commit hash to version
import subprocess
try:
    # NOTE this does not take into account possible unstaged changes, it only reports the current commit
    git_hash = subprocess.check_output(
        ["git", "describe", "--always"], encoding="utf-8"
    )
    # remove trailing newline from hash
    git_hash = git_hash.rstrip("\n")
    mp_version = mp_version + "+" + git_hash
except:
    # NOTE if the git repo contents were downloaded as zip and user doesn't have git installed,
    # commit hash will be unknown
    print("Warning: cannot find git executable or repository, commit hash unknown")
'''

setup(name='moltenprot',
      version=mp_version,
      description='Toolkit for protein (thermal) unfolding analysis.',
      author='Vadim Kotov',
      license='GPLv3',
      url='',# is required
      include_package_data=True,
      packages=['moltenprot'],
      python_requires="<3.11",
      install_requires=[
          'pandas<2.0',
          'numpy<2.0',
          'scipy>=1.10',
          'openpyxl',
          'xlrd',
          'matplotlib>=3.7',
      ],
      extras_require = {
          'gui':['pyqt5'],
          'multiproc' : ['joblib<1.0']
          },
      # shortcuts to be installed system-wide
      entry_points={
          'console_scripts': [
              'moltenprot=moltenprot.__main__:main',
          ],
          'gui_scripts': [
              'moltenprot_gui=moltenprot.__main__:MoltenprotGUI',
          ]
      }
)
