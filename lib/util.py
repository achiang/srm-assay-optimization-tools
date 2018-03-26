from glob import glob


def get_filtered_cwd():
    files = glob('*')
    blacklist = [
        'lib',
        'LICENSE',
        'README.md',
        'SRM_Assay_Optimization.ipynb']
    return [f for f in files if f not in blacklist]
