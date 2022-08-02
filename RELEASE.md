# Publishing a release

This page describes the steps required to author a release of
the `gwosc` Python client.

Notes:

-   `gwosc` uses the
    [stable mainline](https://www.bitsnbites.eu/a-stable-mainline-branching-model-for-git/)
    branching model for releases.
-   All release numbers must follow [Semantic Versioning 2](https://semver.org)
    and include major, minor, and patch numbers, e.g. `1.0.0` rather
    than `1.0` or just `1`.
-   The instructions below presume that you have cloned the `gwosc/client`
    gitlab project with <https://git.ligo.org/gwosc/client.git> configured
    as a `remote` named `upstream`:

    ```bash
    git remote add upstream https://git.ligo.org/gwosc/client.git
    ```

## Step-by-step

### Release notes

All releases should be accompanied by a comprehensive set of release notes,
written using
[GitLab Flavoured Markdown (GLFM)](https://docs.gitlab.com/ee/user/markdown.html)
syntax.
This normally takes the form of minimum summary information, then an itemised
list of changes included in this release relative to the previous release,
grouped by their API-compatibility:

-   _Backwards-incompatible changes_,
-   _Backwards-compatible changes_,
-   _Bug fixes and other changes_.

The list of changes can just be a list of the merge requests associated with
the relevant gitlab milestone, including the `!123` reference and a small
summary, e.g.:

> -   [!123] fix bug in `gwosc.timeline.get_segments`

Include a link to the release itself at the bottom of the release notes.

Full example:

> gwosc 3.0.0
>
> New major release of the GWOSC Python client.
> This is the first release to formally support Python 4.0.0.
>
> Backwards-incompatible changes:
>
> - [!300] remove deprecated thing
> - [!301] drop support for Python 3.10
>
> Backwards-compatible changes:
>
> - [!302] add `gwosc.magic.thing()` function to do magic
>
> Bug fixes and other changes:
>
> - [!303] fix bug in `gwosc.timeline.get_segments`
> - [!304] fix typo in docstring for `gwosc.datasets.find_datasets`
>
> For a full list of changes related to this release, please see
>
> <https://git.ligo.org/gwosc/client/-/releases/v3.0.0>

### Major/minor release

For a major (`X.0.0`) or minor (`X.Y.0`) release:

1.  **Fetch the latest commits for the `upstream/main` branch**:

    ```bash
    git fetch upstream
    git checkout upstream/main
    ```

1.  **Choose the `X.Y` version number**:

    ```bash
    export GWOSC_VERSION="X.Y"
    ```

    e.g.

    ```bash
    export GWOSC_VERSION="1.2"
    ```

1.  **Tag the release**:

    ``` bash
    git tag --sign v${GWOSC_VERSION}.0
    ```

    This will open an editor, into which you should insert the release notes.

1.  **Create a maintenance branch**:

    ``` bash
    git branch release/${GWOSC_VERSION}.x
    ```

1.  **Publish the new tag and the maintenance branch**:

    ``` bash
    git push --signed=if-asked upstream v${GWOSC_VERSION}.0 release/${GWOSC_VERSION}.x
    ```

### Bug-fix release

Bug-fix (patch) releases are handled slightly differently, mainly due to the
use of a `release/X.Y.x` maintenance branch.

1.  **Choose the `X.Y.Z` version number**:

    ```bash
    export GWOSC_VERSION="X.Y.Z"
    ```

    e.g.

    ```bash
    export GWOSC_VERSION="1.2.3"
    ```

1.  **Fetch the latest commits for the `release/X.Y.x` maintenance branch**:

    ``` bash
    git fetch upstream
    git checkout upstream/release/${GWOSC_VERSION%.*}.x
    ```

1.  **Tag the release**:

    ``` bash
    git tag --sign v${GWOSC_VERSION}
    ```

    This will open an editor, into which you should insert the release notes.

1.  **Publish the new tag**:

    ``` bash
    git push --signed=if-asked upstream v${GWOSC_VERSION}
    ```

1.  **Draft a release on GitLab**

    -   Go to <https://git.ligo.org/gwosc/client/-/releases/new>.
    -   Select the new tag from the _Tag name_ dropdown menu.
    -   Use `gwosc X.Y.Z` as the *Release title*.
    -   Copy the release notes into the text box (omitting the title line).

### Distributing the new release package

Package distributions for PyPI, Conda, Debian, and RHEL are done
manually:

#### PyPI

To create a new release on PyPI:

``` bash
# remove old distributions
git clean -dfX
# check out the release tag
git checkout vX.Y.Z
# generate the distributions
python -m build
# upload the distributions to pypi.org
python -m twine upload --sign dist/gwosc-X.Y.Z*
```

#### Conda

Once the PyPI upload has completed, the conda-forge bot will
automatically open a pull request to
[conda-forge/gwosc-feedstock](https://github.com/conda-forge/gwosc-feedstock.git).
Just double-check that the dependencies and tests are up-to-date, then
merge.

### Debian/RHEL

To requests Debian/RHEL packages to be built and for this new version to be
included in the IGWN software repositories,
[open an SCCB request](https://git.ligo.org/computing/sccb/-/issues/new).
