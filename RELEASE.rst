#################
Releasing `gwosc`
#################

This repo follows the `git flow <https://github.com/nvie/gitflow>`__ branching model for releases, meaning all development changes are pushed onto the `develop` branch, and `master` is only updated at release time.
This means that the `master` branch always represents a stable working copy of the package.

So, to release a new version of the package:

#. **Create a release branch using git flow**

   .. code-block:: bash

      $ git flow release start 1.0.0

   and then ``publish`` it, allowing CI to run, and others to contribute:

   .. code-block:: bash

      $ git flow release publish 1.0.0

#. **Wait patiently for the continuous integration to finish**

#. **Announce the release** and ask for final contributions

#. **Finalise the release and push**

   .. code-block:: bash

      $ git flow release finish 1.0.0
      $ git push origin master
      $ git push origin --tags

   .. note::

      The ``git flow release finish`` command will open two prompts, one
      to merge the release branch into `master`, just leave that as is. The
      second prompt is the tag message, please complete this to include the
      release notes for this release.

#. **Draft a release on GitHub**

   * Go to https://github.com/gwpy/gwosc/releases/new
   * Use ``v1.0.0`` as the *Tag version*
   * Use 1.0.0 as the *Release title*
   * Copy the tag message into the text box to serve as release notes
   
#. **Upload the new release to pypi**

   .. code-block: bash
   
      $ rm -rf dist/*
      $ python setup.py sdist
      $ python2.7 bdist_wheel
      $ twine upload dist/losc-1.0.0.*
