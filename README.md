# Python Viewport Overlay Template

Template for a custom Python-based viewport overlay that hooks into OVITO and can easily be shared with other users.

This repository contains a template for creating your own [Python script viewport overlay](https://www.ovito.org/docs/current/reference/viewports/layers/python_script_layer.html#viewport-layers-python-script), 
which can be installed into *OVITO Pro* or the [`ovito`](https://pypi.org/project/ovito/) Python module using *pip*. 

## Getting Started

1. Click the "Use this template" button to create your own repository based on this template.
2. Rename `src/PackageName` to reflect the name of your viewport overlay.
3. Implement your [custom viewport overlay](https://ovito.org/docs/dev/python/introduction/custom_overlays.html) in [`src/PackageName/__init__.py`](src/PackageName/__init__.py). 
4. Fill in the [`pyproject.toml`](pyproject.toml) file. Fields that need to be replaced with your information are enclosed in descriptive `[[field]]` tags. Please make sure to include ovito>=3.9.2 as a dependency. Depending on your needs, you can add additional fields to the `pyproject.toml` file. Information can be found [here](https://setuptools.pypa.io/en/latest/userguide/index.html).
5. Fill in the [`README_Template.md`](README_Template.md) file. Again, the `[[fields]]` placeholders should guide you. Feel free to add other sections like "Images", "Citation", or "References" as needed.
6. Add meaningful examples and data sample files to the `examples` directory to help others understand the use of your viewport overlay.
7. Pick a license for your project and replace the current (MIT) [`LICENSE`](LICENSE) file with your license. If you keep the MIT license, please update the name and year in the current file.
8. Once you're done, rename `README_Template.md` to `README.md`, replacing this file.

## Testing
This repository is configured to enable automated testing using the [pytest](https://docs.pytest.org/en/) framework. Tests are automatically executed after each push to the main branch. To set up and activate automated testing, follow these two steps:

1. Write your tests in the `test/test_viewport_overlay.py` file. You can also use other filenames that adhere to the pytest requirements.
2. Open the `.github/workflows/python-tests.yml` file and remove the `if: ${{ false }}` condition on line 15.

If needed, you can also adjust the operating system and Python versions by modifying the following lines:
```yaml
os: [ubuntu-latest, macos-latest, windows-latest]
python-version: ["3.7", "3.8", "3.9", "3.10", "3.11"]
```

An example can be found [here](https://github.com/nnn911/GenerateRandomSolution).

As of August 16, 2023, according to the [GitHub documentation](https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions), *"GitHub Actions usage is free for standard GitHub-hosted runners in public repositories, and for self-hosted runners."* Please refer to the GitHub documentation if you are uncertain about incurring costs.

