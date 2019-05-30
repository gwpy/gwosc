#################
Releasing `gwosc`
#################

To release a new version of the package:

#. **If this is a major, or minor release (as opposed to a bug-fix release), create a release branch**::

      git checkout -b release/vX.Y

   **Or, if this is a bug-fix release, just check out that branch**::

      git checkout release/vX.Y

#. **Bump versions and add changelog entries in OS packaging files:**

   - `/debian/changelog`
   - `/gwosc.spec`

   and then **commit those**

#. **Publish the release**, allowing CI to run, and others to see it::

      git push -u origin release/vX.Y

#. **Wait patiently for the continuous integration to finish**

#. **Announce the release** and ask for final contributions

#. **Finalise the release and push**::

      git tag --sign vX.Y.Z
      git push --signed=if-asked origin vX.Y.Z

#. **Draft a release on GitHub**

   * Go to https://github.com/gwpy/gwosc/releases/new
   * Use ``vX.Y.Z`` as the *Tag version*
   * Use X.Y.Z as the *Release title*
   * Copy the tag message into the text box to serve as release notes

#. **Upload the new release to pypi**::

      rm -rf dist/*
      python setup.py sdist bdist_wheel
      gpg --armor --detach-sign dist/gwosc-X.Y.Z.tar.gz
      twine upload dist/gwosc-X.Y.Z.*
