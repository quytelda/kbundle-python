===============
kbundle Utility
===============

``kbundle`` is a small utility program for packing Krita bundles
manually and keeping the manifest up to date. This is useful if you
want to manage the files in a bundle outside Krita. For example, you
could keep the bundle contents in a Git repository and quickly
rebuild the ``.bundle`` file whenever you change something.

.. note:: This is a first draft! It works for me, but there's still
	  some quirks to smooth out. Pull requests are welcome :)

Dependencies
============

This program depends on Python 3 and uses only libraries included
with Python.

Usage
=====

The program accepts a subcommand and some number of arguments. You can
optionally specify a bundle directory path with ``--root <DIR>``,
otherwise the current directory is used::

  kbundle [--root <DIR>] <COMMAND> [ARG]...

Recognized commands are ``list``, ``update``, ``pack``, ``unpack``, and ``tag [ls|add|remove]``.

- ``kbundle update`` scans for resource files and updates the
  manifest file (``META-INF/manifest.xml``) accordingly.
- ``kbundle unpack <FILE>`` unzips a Krita bundle file at
  ``<FILE>`` into the current bundle.
- ``kbundle pack <FILE>`` builds a Krita bundle file and writes it
  to ``<FILE>``.
- ``kbundle tag ls <FILE>`` lists the tags currently associated
  with ``<FILE>``. The file must be listed in the manifest and have
  the given tag.
- ``kbundle tag add <TAG> <FILE>`` adds a tag ``<TAG>`` to
  ``<FILE>``. The file must be listed in the manifest and not already
  have the given tag.
- ``kbundle tag remove <TAG> <FILE>`` removes a tag ``<TAG>`` from
  ``<FILE>``. The file must be listed in the manifest and have the
  given tag.

Example
=======

Suppose ``example.bundle`` is an existing bundle file created in
Krita. Since the bundle is actually a ZIP archive, we can unzip the
contents into a local directory::

  $ mkdir example && cd example
  $ kbundle unpack ../example.bundle
  $ ls
  brushes  META-INF  meta.xml  mimetype  paintoppresets  preview.png

The unzipped files are read-only, so we need to change the permissions
before making changes: ``chmod -R u+w *``

Now we can manage the contents of the bundle as files on our
filesystem. For example, we could add a new preset file and rebuild
the bundle::

  $ cp ~/.local/share/krita/paintoppresets/my_preset.kpp ./paintoppresets/
  $ kbundle update # Update the manifest file to include the new preset.
  ... (output elided)
  $ kbundle pack example_v2.bundle

Now we have a new bundle file ``example_v2.bundle`` that includes the
new preset.

We can also inspect, add, or remove tags for resources in the bundle::

  $ kbundle tag ls paintoppresets/my_preset.kpp
  ['Paint']
  $ kbundle tag add Digital paintoppresets/my_preset.kpp
  ['Paint', 'Digital']
  $ kbundle tag remove Paint paintoppresets/my_preset.kpp
  ['Digital']

.. note:: Currently, resources need to be added to the manifest before
	  they can be tagged. Make sure to run ``kbundle update``
	  after adding new resources.
